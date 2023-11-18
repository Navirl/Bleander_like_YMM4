import bpy
import csv
import time
from pathlib import Path
from subprocess import run

csvfile = [text.filepath for text in bpy.data.texts
           if text.filepath.endswith(".csv")][0]

se = bpy.context.scene.sequence_editor
header = "Content-Type: application/json"
fps = bpy.context.scene.render.fps

tmp = Path("/tmp")
pth = tmp /"wav"
pth.mkdir(exist_ok=True, parents=True)

# delete all sequence
for s in se.sequences_all:
     se.sequences.remove(s)

with open(csvfile) as fp:
    for i, ss in enumerate(csv.reader(fp), 1):
        try:
            sec, *mnt = map(float, reversed(("0:" + ss[0]).split(":")))
            speaker = int(ss[1])
            text = ss[2]
        except (IndexError, ValueError):
            print(f"Error at line {i}: {ss}")
            break
        frame_start = int((mnt[0] * 60 + sec) * fps)
        url = f"localhost:50021/{{}}?speaker={speaker}"
        namt = str(tmp / "text.txt")
        with open(namt, "w") as fp:
            fp.write(text)
        cmd = f'curl -s -X POST {url.format("audio_query")} --get --data-urlencode text@{namt}'
        res = run(cmd.split(), capture_output=True)
        namq = str(tmp / "query.json")
        with open(namq, "w") as fp:
            fp.write(res.stdout.decode())
        cmd = f'curl -s -H {header} -X POST -d @{namq} {url.format("synthesis")}'
        res = run(cmd.split(), capture_output=True)
        nama = f"audio{i:03}.wav"
        with open(pth / nama, "wb") as fp:
            fp.write(res.stdout)
        ss = se.sequences.new_sound(nama, str(pth / nama), i * 2, frame_start)
        ss = se.sequences.new_effect(f"txt{i:03}", "TEXT", i * 2 + 1, frame_start, frame_end=ss.frame_final_end)
        ss.text = text
        time.sleep(0.1)
