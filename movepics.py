# from pathlib install Path
# import shutil
# img_types = {".jpeg", ".png",".jpg")
# downloads_folder= Path.home() / "Downloads"
# items moved = 0
# for item in downloads_folder.iterdir():
#     itemname = item.name
#     for type in img_type:
#         if type in item.name:
#                 shutil.shul

from pathlib import Path
img_types = {".jpeg",".jpg",".png"}
downfolder= Path.home() / "Downloads"
picturesfolder= Path.home() / "Pictures"
for item in downfolder.iterdir():
    if item.suffix.lower() in img_types:
        item.rename(picturesfolder / item.name)
