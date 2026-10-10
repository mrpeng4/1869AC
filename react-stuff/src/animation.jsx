import { useEffect, useRef } from 'react'

// characters that fall
var chars = ["♪", "♬", "♫", "."]

// size of each note in pixels, also decides column width
var fontSize = 22

export default function Animation() {
  var canvasRef = useRef(null)

  useEffect(function() {
    var canvas = canvasRef.current
    var ctx = canvas.getContext("2d")

    var drops = []
    var speeds = []
    var counters = []
    var timer = null

    // match canvas to screen size and create the columns
    function setup() {
      canvas.width = canvas.clientWidth
      canvas.height = canvas.clientHeight

      ctx.fillStyle = "#181513"
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      var cols = Math.ceil(canvas.width / fontSize)
      var rows = Math.ceil(canvas.height / fontSize)

      drops = []
      speeds = []
      counters = []
      for (var i = 0; i < cols; i++) {
        drops.push(Math.floor(Math.random() * rows))
        speeds.push(0.25 + Math.random() * 0.6)
        counters.push(0)
      }
    }

    // runs every frame
    function draw() {
      // faint dark layer on top, this creates the fading trail
      ctx.fillStyle = "rgba(24, 21, 19, 0.08)"
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      ctx.font = fontSize + "px terminal, sans-serif"
      ctx.fillStyle = "#d4b28c"

      for (var i = 0; i < drops.length; i++) {
        counters[i] += speeds[i]

        if (counters[i] >= 1) {
          counters[i] = 0

          var note = chars[Math.floor(Math.random() * chars.length)]
          ctx.fillText(note, i * fontSize, drops[i] * fontSize)
          drops[i] = drops[i] + 1

          // after reaching the bottom, sometimes restart from the top
          if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0
          }
        }
      }
    }

    setup()
    timer = setInterval(draw, 40)
    window.addEventListener("resize", setup)

    return function() {
      clearInterval(timer)
      window.removeEventListener("resize", setup)
    }
  }, [])

  return (
    <div className="animation">
      <canvas ref={canvasRef} style={{ width: "100%", height: "100%" }} />
    </div>
  )
}