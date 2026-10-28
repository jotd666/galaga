import subprocess,os,glob,shutil,pathlib,zipfile

progdir = pathlib.Path(__file__).parent.parent.absolute()

gamename = "galaga"
# JOTD path for cranker, adapt to wh :)
os.environ["PATH"] += os.pathsep+r"K:\progs\cli"

cmd_prefix = ["make","-f",os.path.join(progdir,"makefile.am")]

subprocess.check_call(cmd_prefix+["clean"],cwd=os.path.join(progdir,"src"))
for s in ["convert_sounds.py","convert_graphics.py"]:
    subprocess.check_call(["cmd","/c",s],cwd=os.path.join(progdir,"assets","amiga"))

subprocess.check_call(cmd_prefix+["RELEASE_BUILD=1"],cwd=os.path.join(progdir,"src"))
# create archive

distdir = progdir / "dist"
outdir = distdir / f"{gamename}_HD"
flopdir = distdir / f"{gamename}_floppy"

if os.path.isdir(outdir):
    shutil.rmtree(outdir)
outdir.mkdir(exist_ok=True,parents=True)
if os.path.isdir(flopdir):
    shutil.rmtree(flopdir)
flopdir.mkdir(exist_ok=True,parents=True)

for file in ["readme.md",gamename,f"{gamename}.slave"]:
    shutil.copy(os.path.join(progdir,file),outdir)

    shutil.copy(os.path.join(progdir,"assets","amiga","GalagaGlowIcon.info"),os.path.join(outdir,"Galaga500.info"))
    shutil.copy(os.path.join(progdir,"assets","GalaGa Namco.png"),os.path.join(outdir,"boxart.png"))

# pack the file for floppy
subprocess.check_output(["cranker_windows.exe","-f",os.path.join(progdir,gamename),"-o",os.path.join(progdir,f"{gamename}.rnc")])

arcname = progdir / f"{gamename}_HD.lha"
arcname.unlink(missing_ok=True)
cmd = ["lha","-r","a",arcname,"*"]

subprocess.run(cmd,cwd=outdir.parent,check=True)

# create floppy
exename = gamename
shutil.move(progdir/f"{exename}.rnc",progdir/exename)
assets = progdir /"assets"/"amiga"


xtra_dir = flopdir/"xtra"
xtra_dir.mkdir(exist_ok=True)
shutil.copy(assets/f"disk.info",xtra_dir)

with (xtra_dir/"floppy").open("w"):
    pass

shutil.copy(progdir / "readme.md",xtra_dir)


adf_name = "Galaga.adf"
#cmd = ["gadf","-i","galaga","-a",adf_name,"-l","galaga","readme.md","disk.info"]
cmd = ["exe2adf","--add21k","-i",exename,"-a",adf_name,"-l",gamename.title(),"-d",xtra_dir]
subprocess.run(cmd,cwd=progdir)

# create a .zip for the floppy

with zipfile.ZipFile(progdir / "Galaga_adf.zip",mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
    zf.write(progdir/adf_name,arcname=adf_name)
os.remove(progdir/adf_name)
