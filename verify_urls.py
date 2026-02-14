"""
Interactive URL Verification Script
Opens each ground truth URL in Chrome and asks user to verify it matches the task.
Usage: python verify_urls.py
"""
import csv
import json
import os
import sys
import webbrowser
import time

CSV_FILE = os.path.join(os.path.dirname(__file__), "navi_bench", "zillow", "zillow_benchmark_tasks.csv")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "navi_bench", "zillow", "url_verification_results.csv")

def main():
    # Load tasks
    with open(CSV_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    correct = []
    incorrect = []
    skipped = []

    # Check if we have a resume point
    start_idx = 0
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, encoding="utf-8") as f:
            done = list(csv.DictReader(f))
        if done:
            start_idx = len(done)
            correct = [r for r in done if r["result"] == "correct"]
            incorrect = [r for r in done if r["result"] == "incorrect"]
            skipped = [r for r in done if r["result"] == "skipped"]
            print(f"\n  Resuming from task {start_idx}/{total}")
            print(f"  So far: {len(correct)} correct, {len(incorrect)} incorrect, {len(skipped)} skipped\n")

    print("=" * 70)
    print("  ZILLOW GROUND TRUTH URL VERIFICATION")
    print("=" * 70)
    print(f"  Total tasks: {total}")
    print(f"  Starting from: {start_idx}")
    print()
    print("  For each task:")
    print("    - The URL will open in Chrome")
    print("    - Check if Zillow shows the correct search")
    print("    - Type:  y = correct,  n = incorrect,  s = skip,  q = quit")
    print("=" * 70)
    input("\n  Press ENTER to begin...\n")

    # Open results file for appending
    write_header = not os.path.exists(RESULTS_FILE) or start_idx == 0
    results_fp = open(RESULTS_FILE, "a" if start_idx > 0 else "w", newline="", encoding="utf-8")
    writer = csv.writer(results_fp)
    if write_header:
        writer.writerow(["idx", "task_id", "task", "l2_category", "difficulty", "result", "notes"])

    try:
        for i in range(start_idx, total):
            row = rows[i]
            config = json.loads(row["task_generation_config_json"])
            gt_url = config["ground_truth_url"]
            task_text = config["task"]
            l2 = row["l2_category"]
            diff = row["suggested_difficulty"]

            print(f"\n{'─' * 70}")
            print(f"  [{i+1}/{total}]  {row['task_id']}")
            print(f"  Category:   {l2}")
            print(f"  Difficulty: {diff}")
            print(f"{'─' * 70}")
            print(f"\n  TASK: {task_text}\n")
            print(f"  Opening in Chrome...")

            # Open URL in default browser
            webbrowser.open(gt_url)
            time.sleep(1.5)  # Give browser time to open

            print(f"\n  Does the Zillow page match the task description above?")
            while True:
                choice = input("  [y]es / [n]o / [s]kip / [q]uit: ").strip().lower()
                if choice in ("y", "n", "s", "q"):
                    break
                print("  Invalid input. Please enter y, n, s, or q.")

            if choice == "q":
                print("\n  Quitting. Progress saved — you can resume later.\n")
                break

            notes = ""
            if choice == "n":
                notes = input("  What's wrong? (optional, press Enter to skip): ").strip()
                result = "incorrect"
                incorrect.append({"idx": i, "task_id": row["task_id"]})
            elif choice == "s":
                result = "skipped"
                skipped.append({"idx": i, "task_id": row["task_id"]})
            else:
                result = "correct"
                correct.append({"idx": i, "task_id": row["task_id"]})

            writer.writerow([i, row["task_id"], task_text, l2, diff, result, notes])
            results_fp.flush()

            # Show running tally
            checked = len(correct) + len(incorrect) + len(skipped)
            print(f"\n  Running tally: {len(correct)} ✓  {len(incorrect)} ✗  {len(skipped)} ⊘  ({checked}/{total} checked)")

    finally:
        results_fp.close()

    # Final summary
    print(f"\n{'=' * 70}")
    print(f"  VERIFICATION COMPLETE")
    print(f"{'=' * 70}")
    print(f"  ✓ Correct:   {len(correct)}")
    print(f"  ✗ Incorrect: {len(incorrect)}")
    print(f"  ⊘ Skipped:   {len(skipped)}")
    print(f"  Total:       {len(correct) + len(incorrect) + len(skipped)}/{total}")
    print(f"  Accuracy:    {len(correct)/(len(correct)+len(incorrect))*100:.1f}%" if (len(correct)+len(incorrect)) > 0 else "")
    print(f"\n  Results saved to: {RESULTS_FILE}")

    if incorrect:
        print(f"\n  ✗ INCORRECT TASKS:")
        for item in incorrect:
            print(f"    - {item['task_id']}")

    print()


if __name__ == "__main__":
    main()
