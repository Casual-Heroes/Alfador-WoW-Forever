"""Local-only Source04 retest window; no game input, network or automatic logging."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import tkinter as tk
from tkinter import ttk
import uuid

READER_SHA256 = "94dc66713b786c5b88889b5b80e218fd969e3cf3566a8a1aa6847183ac8fa38a"
READER = Path(__file__).with_name("transfer_marker_tail.py")
if hashlib.sha256(READER.read_bytes()).hexdigest() != READER_SHA256:
    raise SystemExit("Reader pin mismatch; no log opened")
from transfer_marker_tail import MarkerTail, POLL_SECONDS

class TestWindow:
    def __init__(self, root, game_root):
        self.root, self.game_root = root, game_root
        self.reader = self.output = None
        self.finished = False
        root.title("Alfador-wow - local 45-second transfer test")
        root.geometry("620x440")
        root.attributes("-topmost", True)
        ttk.Label(root, text="Prepare in WoW first. Paste the NEW session label here.").pack(pady=8)
        self.session = ttk.Entry(root, width=42)
        self.session.pack()
        self.button = ttk.Button(root, text="Show READY and begin 45-second reader", command=self.begin)
        self.button.pack(pady=8)
        self.status = tk.StringVar(value="IDLE - no chat log open")
        ttk.Label(root, textvariable=self.status, font=("Segoe UI", 16, "bold"), wraplength=590).pack(pady=10)
        self.clock = tk.StringVar(value="Elapsed 0.00 s | Received 0 / 8")
        ttk.Label(root, textvariable=self.clock, font=("Segoe UI", 13)).pack()
        ttk.Label(root, text="After READY, immediately enter /alfadortransfertest start in WoW.\nKeep this window visible. Do not reload or log out.\nFor send-to-receipt delay, retain a local screen recording of BOTH\nthe SEND messages and this elapsed clock. Without it, latency is unknown.", wraplength=590).pack(pady=12)
        self.details = tk.Text(root, height=6, width=72, state="disabled")
        self.details.pack(padx=10, pady=5)
        root.protocol("WM_DELETE_WINDOW", self.close)

    def record(self, event):
        self.output.write(json.dumps(event, sort_keys=True) + "\n")
        self.output.flush()

    def begin(self):
        if self.finished or self.reader is not None:
            return
        try:
            reader = MarkerTail(self.game_root, self.session.get().strip())
        except (OSError, ValueError):
            self.status.set("NOT READY - invalid session or log unavailable")
            return
        try:
            folder = Path(__file__).resolve().parents[1] / "local-evidence" / "2026-11-20-source04-local-ready-retest"
            folder.mkdir(parents=True, exist_ok=True)
            output = (folder / ("reader-" + uuid.uuid4().hex + ".jsonl")).open("x", encoding="utf-8")
        except OSError:
            reader.close()
            self.status.set("NOT READY - cannot save sanitized receipt")
            return
        self.reader, self.output = reader, output
        self.button.configure(state="disabled")
        self.session.configure(state="disabled")
        self.record(reader.ready_event())
        self.deadline = reader.started_monotonic + 45.0
        self.status.set("READY - run start in WoW NOW")
        self.root.after(0, self.poll)

    def poll(self):
        if self.finished:
            return
        if time.monotonic() >= self.deadline:
            self.finish()
            return
        try:
            for event in self.reader.poll():
                self.record(event)
                self.details.configure(state="normal")
                description = "Receipt seq=" + str(event["sequence"]) if "sequence" in event else event["event"]
                self.details.insert("end", description + " at elapsed " + format(time.monotonic() - self.reader.started_monotonic, ".2f") + " s\n")
                self.details.see("end")
                self.details.configure(state="disabled")
            elapsed = time.monotonic() - self.reader.started_monotonic
            self.clock.set("Elapsed %.2f s | Received %d / 8 | Remaining %.1f s" % (elapsed, self.reader.receipt_count, max(0,45-elapsed)))
            if self.reader.closed:
                self.finish()
                return
        except (OSError, ValueError):
            self.reader.terminal_reason = "reader-measurement-failed"
            self.finish()
            return
        self.root.after(round(POLL_SECONDS * 1000), self.poll)

    def finish(self, cancelled=False):
        if self.finished:
            return
        self.finished = True
        if self.reader is not None:
            if cancelled:
                self.reader.terminal_reason = "owner-closed-window"
            if not self.reader.closed:
                self.reader.close()
            self.record(self.reader.summary())
            self.output.close()
            self.status.set("DONE - %d / 8 received; restore prior logging state" % self.reader.receipt_count)
        else:
            self.status.set("CLOSED - no reader run")

    def close(self):
        self.finish(cancelled=True)
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forever-root", required=True)
    args = parser.parse_args()
    root = tk.Tk()
    TestWindow(root, args.forever_root)
    root.mainloop()

if __name__ == "__main__":
    main()
