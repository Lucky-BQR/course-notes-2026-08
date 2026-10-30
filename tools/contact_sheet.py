from pathlib import Path
from PIL import Image,ImageDraw
folder=Path(__file__).resolve().parents[1]/'qa'
pages=sorted(folder.glob('page-*.png'))
for start in range(0,len(pages),20):
    group=pages[start:start+20]
    canvas=Image.new('RGB',(1050,((len(group)+4)//5)*310),'#e7e7e7')
    for i,p in enumerate(group):
        im=Image.open(p);im.thumbnail((200,285))
        canvas.paste(im,((i%5)*210,(i//5)*310+20))
        ImageDraw.Draw(canvas).text(((i%5)*210+4,(i//5)*310+4),str(start+i+1),fill='black')
    canvas.save(folder/f'contact-{start//20+1}.png')
print('Rendered pages:',len(pages))
