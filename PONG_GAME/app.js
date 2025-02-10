import Hyperswarm from "hyperswarm"
import crypto from "hypercore-crypto"
import b4a from "b4a"

const swarm = new Hyperswarm()

// Game constants with corrected variable names
const CANVAS_WIDTH = 600
const CANVAS_HEIGHT = 400
const PADDLE_WIDTH = 10
const PADDLE_HEIGHT = 100
const BALL_SIZE = 10
const PADDLE_SPEED = 15
const BALL_SPEED = 3

class PongGame {
  constructor(canvas, playerId) {
    this.canvas = canvas
    this.ctx = canvas.getContext("2d")
    this.playerId = playerId
    this.players = new Map()
    this.ball = { 
      x: CANVAS_WIDTH / 2, 
      y: CANVAS_HEIGHT / 2, 
      dx: BALL_SPEED, 
      dy: BALL_SPEED 
    }
    this.scores = {}
    this.isHost = false

    this.ballImage = new Image()
    this.ballImage.src = "/logo.svg?height=20&width=20"
    this.ballLoaded = false
    this.ballImage.onload = () => {
      this.ballLoaded = true
      this.startGame()
    }

    // Set canvas size
    this.canvas.width = CANVAS_WIDTH
    this.canvas.height = CANVAS_HEIGHT
  }

  startGame() {
    this.gameLoop()
  }

  addPlayer(id) {
    if (this.players.size >= 2) return
    const isLeft = this.players.size === 0
    const x = isLeft ? 0 : CANVAS_WIDTH - PADDLE_WIDTH
    const y = CANVAS_HEIGHT / 2 - PADDLE_HEIGHT / 2
    this.players.set(id, { x, y, score: 0, isLeft })
    this.scores[id] = 0
    
    if (isLeft) {
      this.isHost = true
    }
  }

  movePlayer(id, direction) {
    const player = this.players.get(id)
    if (player) {
      player.y += direction * PADDLE_SPEED
      player.y = Math.max(0, Math.min(CANVAS_HEIGHT - PADDLE_HEIGHT, player.y))
    }
  }

  updateBall() {
    if (!this.isHost) return

    this.ball.x += this.ball.dx
    this.ball.y += this.ball.dy

    // Wall collisions
    if (this.ball.y <= 0 || this.ball.y + BALL_SIZE > CANVAS_HEIGHT) {
      this.ball.dy = -this.ball.dy
    }

    // Paddle collisions
    for (const [id, player] of this.players) {
      const paddleLeft = player.x
      const paddleRight = player.x + PADDLE_WIDTH
      const paddleTop = player.y
      const paddleBottom = player.y + PADDLE_HEIGHT

      if (
        (this.ball.dx < 0 && 
         this.ball.x <= paddleRight &&
         this.ball.x + BALL_SIZE >= paddleLeft &&
         this.ball.y + BALL_SIZE >= paddleTop &&
         this.ball.y <= paddleBottom) ||
        (this.ball.dx > 0 &&
         this.ball.x + BALL_SIZE >= paddleLeft &&
         this.ball.x <= paddleRight &&
         this.ball.y + BALL_SIZE >= paddleTop &&
         this.ball.y <= paddleBottom)
      ) {
        this.ball.dx = -this.ball.dx
        this.ball.dy += (Math.random() - 0.5) * 2
        this.ball.dy = Math.max(Math.min(this.ball.dy, BALL_SPEED), -BALL_SPEED)
        break
      }
    }

    // Score points
    if (this.ball.x <= 0 || this.ball.x + BALL_SIZE >= CANVAS_WIDTH) {
      const scoringPlayer = this.ball.x <= 0 
        ? Array.from(this.players.values()).find(p => !p.isLeft)
        : Array.from(this.players.values()).find(p => p.isLeft)
      
      if (scoringPlayer) {
        const scoringPlayerId = Array.from(this.players.entries())
          .find(([, p]) => p === scoringPlayer)[0]
        this.scores[scoringPlayerId]++
        this.resetBall()
      }
    }
  }

  resetBall() {
    this.ball = {
      x: CANVAS_WIDTH / 2 - BALL_SIZE / 2,
      y: CANVAS_HEIGHT / 2 - BALL_SIZE / 2,
      dx: BALL_SPEED * (Math.random() > 0.5 ? 1 : -1),
      dy: BALL_SPEED * (Math.random() > 0.5 ? 1 : -1)
    }
  }

  draw() {
    this.ctx.fillStyle = "black"
    this.ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    // Draw center line
    this.ctx.setLineDash([5, 15])
    this.ctx.beginPath()
    this.ctx.moveTo(CANVAS_WIDTH / 2, 0)
    this.ctx.lineTo(CANVAS_WIDTH / 2, CANVAS_HEIGHT)
    this.ctx.strokeStyle = "white"
    this.ctx.stroke()

    // Draw paddles
    this.ctx.fillStyle = "white"
    for (const player of this.players.values()) {
      this.ctx.fillRect(player.x, player.y, PADDLE_WIDTH, PADDLE_HEIGHT)
    }

    // Draw ball
    if (this.ballLoaded) {
      this.ctx.drawImage(this.ballImage, this.ball.x, this.ball.y, BALL_SIZE, BALL_SIZE)
    }

    // Draw scores
    this.ctx.font = "24px monospace"
    const players = Array.from(this.players.keys())
    if (players.length === 2) {
      this.ctx.fillText(`Score: ${this.scores[players[0]]}`, CANVAS_WIDTH / 4, 30)
      this.ctx.fillText(`Score: ${this.scores[players[1]]}`, (CANVAS_WIDTH / 4) * 3, 30)
    }
  }

  gameLoop() {
    this.updateBall()
    this.draw()
    requestAnimationFrame(() => this.gameLoop())
  }

  getState() {
    return {
      ball: this.ball,
      players: Array.from(this.players.entries()),
      scores: this.scores
    }
  }

  setState(state) {
    this.ball = state.ball
    this.players = new Map(state.players)
    this.scores = state.scores
  }
}

// UI and networking setup
const createGameBtn = document.getElementById("create-game")
const joinForm = document.getElementById("join-form")
const loadingElement = document.getElementById("loading")
const gameElement = document.getElementById("game")
const canvas = document.getElementById("pong-canvas")

createGameBtn.addEventListener("click", createGame)
joinForm.addEventListener("submit", joinGame)

let game = null
let playerId = null
const keyState = {}

async function createGame() {
  const topicBuffer = crypto.randomBytes(32)
  const topic = b4a.toString(topicBuffer, "hex")
  document.getElementById("join-game-topic").value = topic
  await setupGame(topicBuffer)
}

async function joinGame(e) {
  e.preventDefault()
  const topicStr = document.getElementById("join-game-topic").value
  const topicBuffer = b4a.from(topicStr, "hex")
  await setupGame(topicBuffer)
}

async function setupGame(topicBuffer) {
  try {
    showLoading()
    await joinSwarm(topicBuffer)
    playerId = b4a.toString(swarm.keyPair.publicKey, "hex").slice(0, 6)
    
    if (!game) {
      game = new PongGame(canvas, playerId)
      game.addPlayer(playerId)
    } else {
      game.addPlayer(playerId)
    }
    
    showGame(topicBuffer)
    updatePeerCount()
  } catch (error) {
    console.error("Error setting up game:", error)
    showSetup()
  }
}

async function joinSwarm(topicBuffer) {
  const discovery = swarm.join(topicBuffer, { client: true, server: true })
  await discovery.flushed()
}

function showLoading() {
  document.getElementById("setup").classList.add("hidden")
  loadingElement.classList.remove("hidden")
}

function showGame(topicBuffer) {
  const topic = b4a.toString(topicBuffer, "hex")
  document.getElementById("game-topic").textContent = topic
  loadingElement.classList.add("hidden")
  gameElement.classList.remove("hidden")
}

function showSetup() {
  loadingElement.classList.add("hidden")
  gameElement.classList.add("hidden")
  document.getElementById("setup").classList.remove("hidden")
}

// Input handling
document.addEventListener("keydown", e => {
  keyState[e.key] = true
})

document.addEventListener("keyup", e => {
  keyState[e.key] = false
})

function updatePlayerPosition() {
  if (!game || !playerId) return
  
  if (keyState.ArrowUp) {
    game.movePlayer(playerId, -1)
  }
  if (keyState.ArrowDown) {
    game.movePlayer(playerId, 1)
  }
}

// Network synchronization
swarm.on("connection", (peer) => {
  const peerId = b4a.toString(peer.remotePublicKey, "hex").slice(0, 6)
  
  if (game && !game.players.has(peerId)) {
    game.addPlayer(peerId)
  }

  peer.on("data", (data) => {
    try {
      const state = JSON.parse(data.toString())
      game.setState(state)
    } catch (error) {
      console.error("Error parsing message:", error)
    }
  })

  peer.on("close", () => {
    if (game) game.players.delete(peerId)
    updatePeerCount()
  })
})

function updatePeerCount() {
  document.getElementById("peers-count").textContent = swarm.connections.size + 1
}

// Game state sync loop
setInterval(() => {
  if (!game) return
  
  updatePlayerPosition()
  
  if (game.isHost) {
    const state = game.getState()
    const data = JSON.stringify(state)
    for (const peer of swarm.connections) {
      peer.write(data)
    }
  }
}, 1000 / 60)