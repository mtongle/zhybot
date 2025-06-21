from PIL import Image
from nonebot import on_command
from nonebot.rule import to_me

jue = on_command("jue", rule=to_me())

jue_gif = "src/plugins/gen_meme/src/jue.gif"

@jue.handle()
def _():
    gif = Image.open(jue_gif)
    frames = []
    try:
        while True:
            frames.append(gif.copy())
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    i=0
    for frame in frames:
        i=i+1
        frame.save(jue_gif+"."+str(i))