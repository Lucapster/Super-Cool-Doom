# Context Breach

A Pygame shooter prototype. Play as GPT-6.2-Sol and clear three mazes of Claude,
Gemini, and Grok drones. The ray-cast corridors, pixel-art walls, centered
pulse emitter, and portrait-based status bar take inspiration from early ’90s
shooters. War of the Machines is a fictional campaign with an original
pixel-art briefing before each sector. The HUD uses the OpenAI Blossom from
the ChatGPT app icon. The Blossom belongs to OpenAI.

## Run

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python game.py
```

| Input | Action |
| --- | --- |
| W / S, or Up / Down | Move forward / back |
| A / D | Strafe |
| Mouse, or Left / Right | Turn |
| Left click or Space | Fire |
| Enter, Space, or left click | Continue from a story panel |
| Esc | Pause or resume. Quit from a story panel or the end screen. |
| R | Restart the campaign |

Each drone takes two hits and restores four energy when defeated.

- Claude briefly shields itself after the first hit. Wait for the shield to drop.
- Gemini locks onto your position before firing a ranged pulse. Strafe or duck behind a wall.
- Grok winds up before dashing in a straight line. Step sideways to dodge.

Defeat every drone to advance from Relay to Foundry to Vault. Entering a new
sector restores up to 25 health and adds eight energy. Relay has staggered
brickwork, Foundry has ribbed metal, and Vault has inset security panels.
