from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];out=root/'qa/daily-renders';out.mkdir(exist_ok=True)
paths=sorted((root/'docs/downloads/daily').glob('*.pdf'))
def render(p):
    subprocess.run(['pdftoppm','-r','55','-png',str(p),str(out/p.stem)],check=True)
    images=sorted(out.glob(p.stem+'-*.png'));width=240;height=330
    sheet=Image.new('RGB',(5*width,((len(images)+4)//5)*height),'#e8edf0')
    for i,path in enumerate(images):
        im=Image.open(path);im.thumbnail((width-12,height-25));x=(i%5)*width;y=(i//5)*height
        sheet.paste(im,(x,y+20));ImageDraw.Draw(sheet).text((x+4,y+3),f'{p.stem} / {i+1}',fill='black')
    sheet.save(root/'qa'/f'daily-pdf-{p.stem}.png')
    return dict(day=p.stem,rendered=len(images))
with ThreadPoolExecutor(max_workers=3) as pool:
    for result in pool.map(render,paths):print(result,flush=True)
