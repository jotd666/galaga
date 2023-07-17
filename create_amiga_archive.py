import subprocess,zipfile,os

progdir = os.path.abspath(os.path.dirname(__file__))

# JOTD path for cranker, adapt to wh :)
os.environ["PATH"] += os.pathsep+r"K:\progs\cli"

cmd_prefix = ["make","-f",os.path.join(progdir,"makefile.am")]

subprocess.check_call(cmd_prefix+["clean"],cwd=os.path.join(progdir,"src"))

subprocess.check_call(cmd_prefix+["RELEASE_BUILD=1"],cwd=os.path.join(progdir,"src"))
# create archive
with zipfile.ZipFile(os.path.join(progdir,"Pengo500_HD.zip"),"w",compression=zipfile.ZIP_DEFLATED) as zf:
    for file in ["readme.md","instructions.txt","pengo","pengo.slave"]:
        zf.write(os.path.join(progdir,file),arcname=file)

    zf.write(os.path.join(progdir,"assets","amiga","Pengo.info"),"Pengo.info")
    zf.write(os.path.join(progdir,"assets","amiga","boxart.png"),"boxart.png")

# pack the file for floppy
subprocess.check_output(["cranker_windows.exe","-f",os.path.join(progdir,"pengo"),"-o",os.path.join(progdir,"pengo.rnc")])