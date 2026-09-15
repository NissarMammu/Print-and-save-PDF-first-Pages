import os
import time
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter


def select_folder():
    folder = filedialog.askdirectory(
        title="Select folder containing PDF files"
    )

    if folder:
        folder_var.set(folder)
        check_pdfs(folder)


def select_output_folder():
    folder = filedialog.askdirectory(
        title="Select folder to save the combined PDF"
    )

    if folder:
        output_folder_var.set(folder)


def check_pdfs(folder):
    pdf_files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ]

    pdf_files.sort()

    count_var.set(f"{len(pdf_files)} PDF file(s) found")


def get_pdf_list(folder):
    pdf_files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ]
    pdf_files.sort()
    return pdf_files


def process_files():
    folder = folder_var.get()

    if not folder or not os.path.isdir(folder):
        messagebox.showerror(
            "Error",
            "Please select a valid PDF folder."
        )
        return

    do_print = print_var.get()
    do_save = save_var.get()

    if not do_print and not do_save:
        messagebox.showwarning(
            "Nothing to do",
            "Please tick at least one option: Print and/or Save as combined PDF."
        )
        return

    output_folder = output_folder_var.get()

    if do_save and (not output_folder or not os.path.isdir(output_folder)):
        messagebox.showerror(
            "Error",
            "Please select a valid output folder for the combined PDF."
        )
        return

    pdf_files = get_pdf_list(folder)

    if not pdf_files:
        messagebox.showwarning(
            "No PDFs",
            "No PDF files were found in the selected folder."
        )
        return

    action_text = []
    if do_print:
        action_text.append("PRINT page 1 of each PDF")
    if do_save:
        action_text.append("SAVE all first pages into ONE combined PDF")

    answer = messagebox.askyesno(
        "Confirm",
        f"{len(pdf_files)} PDF file(s) found.\n\n"
        + " and\n".join(action_text)
        + "\n\nDo you want to continue?"
    )

    if not answer:
        return

    printed = 0
    failed = []
    combined_writer = PdfWriter() if do_save else None
    added_to_combined = 0

    # Temp folder used only if printing (per-file first-page copies)
    temp_folder = tempfile.mkdtemp(prefix="pdf_first_page_") if do_print else None

    for filename in pdf_files:
        pdf_path = os.path.join(folder, filename)

        try:
            reader = PdfReader(pdf_path)

            if len(reader.pages) == 0:
                failed.append(f"{filename} - No pages")
                continue

            first_page = reader.pages[0]

            # --- Add to combined PDF ---
            if do_save:
                combined_writer.add_page(first_page)
                added_to_combined += 1

            # --- Print individually ---
            if do_print:
                writer = PdfWriter()
                writer.add_page(first_page)

                first_page_pdf = os.path.join(
                    temp_folder,
                    "FIRST_PAGE_" + filename
                )

                with open(first_page_pdf, "wb") as output:
                    writer.write(output)

                os.startfile(first_page_pdf, "print")
                printed += 1

                # Small delay so the spooler/PDF viewer isn't flooded
                time.sleep(1.5)

        except Exception as e:
            failed.append(f"{filename} - {str(e)}")

    combined_path = None
    if do_save and added_to_combined > 0:
        combined_path = os.path.join(output_folder, "COMBINED_FIRST_PAGES.pdf")
        with open(combined_path, "wb") as f:
            combined_writer.write(f)

    message = f"PDF files processed: {len(pdf_files)}\n"

    if do_print:
        message += f"First pages sent to printer: {printed}\n"

    if do_save:
        if combined_path:
            message += f"Combined PDF saved to:\n{combined_path}\n"
        else:
            message += "Combined PDF was NOT created (no valid pages).\n"

    message += f"Failed: {len(failed)}"

    if failed:
        message += "\n\nFailed files:\n"
        message += "\n".join(failed[:10])

    messagebox.showinfo("Process Complete", message)


# -------------------------
# GUI
# -------------------------

root = tk.Tk()

root.title("PDF First Page Tool")
root.geometry("640x430")
root.resizable(False, False)

title = tk.Label(
    root,
    text="PDF First Page Tool",
    font=("Arial", 18, "bold")
)
title.pack(pady=15)

# Source folder
folder_var = tk.StringVar()

folder_entry = tk.Entry(root, textvariable=folder_var, width=70)
folder_entry.pack(pady=5)

select_button = tk.Button(
    root,
    text="Select PDF Source Folder",
    width=30,
    height=2,
    command=select_folder
)
select_button.pack(pady=5)

count_var = tk.StringVar(value="No folder selected")
count_label = tk.Label(root, textvariable=count_var, font=("Arial", 11))
count_label.pack(pady=5)

# Output folder (for combined PDF)
output_folder_var = tk.StringVar()

output_entry = tk.Entry(root, textvariable=output_folder_var, width=70)
output_entry.pack(pady=5)

output_button = tk.Button(
    root,
    text="Select Output Folder (for combined PDF)",
    width=32,
    height=2,
    command=select_output_folder
)
output_button.pack(pady=5)

# Options
options_frame = tk.Frame(root)
options_frame.pack(pady=10)

print_var = tk.BooleanVar(value=True)
save_var = tk.BooleanVar(value=True)

print_check = tk.Checkbutton(
    options_frame, text="Print page 1 of each PDF",
    variable=print_var, font=("Arial", 11)
)
print_check.grid(row=0, column=0, padx=15)

save_check = tk.Checkbutton(
    options_frame, text="Save combined PDF (all first pages)",
    variable=save_var, font=("Arial", 11)
)
save_check.grid(row=0, column=1, padx=15)

# Run button
run_button = tk.Button(
    root,
    text="RUN",
    width=35,
    height=2,
    command=process_files
)
run_button.pack(pady=15)

info = tk.Label(
    root,
    text="Print sends page 1 of each PDF to the default printer.\n"
         "Save merges page 1 of every PDF into one combined PDF file.\n"
         "Powered by Nissar.",
    font=("Arial", 9),
    justify="center"
)
info.pack(pady=5)

root.mainloop()
