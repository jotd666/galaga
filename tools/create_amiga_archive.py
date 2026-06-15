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

outdir = progdir/"dist"/f"{gamename}_HD"

if os.path.isdir(outdir):
    shutil.rmtree(outdir)

outdir.mkdir(exist_ok=True,parents=True)

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

shutil.copy(assets/"disk.info",progdir)
adf_name = "Galaga.adf"
cmd = ["gadf","-i","galaga","-a",adf_name,"-l","galaga","readme.md","disk.info"]
subprocess.run(cmd,cwd=progdir)

# create a .zip for the floppy

with zipfile.ZipFile(progdir / "Galaga_adf.zip",mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
    zf.write(progdir/adf_name,arcname=adf_name)
os.remove(progdir/adf_name)
