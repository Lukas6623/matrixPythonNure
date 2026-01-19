<h1 align="center">🟦 LED Matrix Animation Editor (16×16)</h1>

<p align="center">
  <b>Python + PyQt6 visual editor for creating animations for dual 16×16 LED matrices</b>
</p>

<hr>

<h2>📌 About the Project</h2>

<p>
This project is a <b>graphical animation editor</b> designed to create, edit, preview,
and export animations for <b>two 16×16 LED matrices</b> (LEFT and RIGHT).
</p>

<p>
It is especially useful for:
</p>

<ul>
  <li>ESP32 / Arduino LED matrix projects</li>
  <li>Robotic eyes / face animations</li>
  <li>Scrolling text animations</li>
  <li>Custom pixel-based effects</li>
</ul>

<hr>

<h2>✨ Features</h2>

<ul>
  <li>🟩 Two independent 16×16 pixel matrices</li>
  <li>🖱️ Mouse-based pixel drawing (left click = ON, right click = OFF)</li>
  <li>🎞️ Frame-based animation system</li>
  <li>📝 Scrolling text generator using a 4×7 ASCII font</li>
  <li>📂 JSON import/export for microcontrollers</li>
  <li>▶️ Animation preview with adjustable FPS</li>
  <li>🖼️ Frame gallery & frame editor</li>
  <li>💾 Session-based workflow with autosave support</li>
</ul>

<hr>

<h2>🧩 JSON Output Format</h2>

<p>The exported animation file looks like this:</p>

<pre>
{
  "fps": 12,
  "loop": true,
  "frames": [
    {
      "left":  [0,1,0,1,...],
      "right": [1,0,1,0,...]
    }
  ]
}
</pre>

<p>
Each matrix frame contains <b>256 values (16×16)</b>, where:
</p>

<ul>
  <li><b>1</b> = LED ON</li>
  <li><b>0</b> = LED OFF</li>
</ul>

<hr>

<h2>🚀 How to Run</h2>

<pre>
pip install PyQt6
python main.py
</pre>

<p>
Make sure the file <code>font_7x4.py</code> is present in the same directory.
</p>

<hr>

<h2>🖥️ Interface Overview</h2>

<ul>
  <li><b>LEFT / RIGHT</b> — LED matrices</li>
  <li><b>Add Frame</b> — saves current pixels as a new frame</li>
  <li><b>Start / Stop</b> — preview animation</li>
  <li><b>Gallery</b> — preview all frames</li>
  <li><b>Edit Frame</b> — modify an existing frame</li>
  <li><b>Save / Load JSON</b> — export/import animations</li>
</ul>

<hr>

<h2>🛠️ Technologies Used</h2>

<ul>
  <li>Python 3</li>
  <li>PyQt6</li>
  <li>JSON</li>
</ul>

<hr>

<h2>📜 License</h2>

<p>
This project is open-source and free to use for educational and non-commercial purposes.
</p>

<hr>

<p align="center">
  🔧 Created for LED matrix animation experiments and embedded projects
</p>
