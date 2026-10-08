"""
SafaiOS Granular Commit Engine
Splits untracked candidate files in data/incoming/ into 35 clean, granular commits
and pushes them to GitHub.
"""
import os
import subprocess
from pathlib import Path

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}\nError: {result.stderr}")
    return result.stdout.strip()

def commit_granular():
    pilot_img_dir = Path("data/incoming/open_images_staging/images")
    pilot_lbl_dir = Path("data/incoming/open_images_staging/labels")
    
    batch_img_dir = Path("data/incoming/large_batch_staging/images")
    batch_lbl_dir = Path("data/incoming/large_batch_staging/labels")

    all_pairs = []
    
    if pilot_img_dir.exists():
        for img_p in sorted(pilot_img_dir.glob("*.jpg")):
            lbl_p = pilot_lbl_dir / f"{img_p.stem}.txt"
            all_pairs.append((img_p, lbl_p, "pilot"))
            
    if batch_img_dir.exists():
        for img_p in sorted(batch_img_dir.glob("*.jpg")):
            lbl_p = batch_lbl_dir / f"{img_p.stem}.txt"
            all_pairs.append((img_p, lbl_p, "large_batch"))

    print(f"Total candidate pairs to commit: {len(all_pairs)}")

    chunk_size = 6  # 194 / 6 ~= 33 chunks
    chunks = [all_pairs[i:i + chunk_size] for i in range(0, len(all_pairs), chunk_size)]
    
    print(f"Will create {len(chunks)} granular commits.")

    for idx, chunk in enumerate(chunks, 1):
        files_to_add = []
        for img_p, lbl_p, source in chunk:
            files_to_add.append(str(img_p))
            if lbl_p.exists():
                files_to_add.append(str(lbl_p))

        add_cmd = f"git add {' '.join(files_to_add)}"
        run_cmd(add_cmd)
        
        msg = f"feat(dataset): stage Open Images candidate batch {idx:02d}/{len(chunks):02d} ({len(chunk)} images & labels)"
        commit_cmd = f'git commit -m "{msg}"'
        out = run_cmd(commit_cmd)
        print(f"Commit {idx}/{len(chunks)}: {msg}")

    print("\nAll granular commits created locally!")

if __name__ == "__main__":
    commit_granular()
