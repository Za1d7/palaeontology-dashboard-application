import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

DB_NAME = "palaeontology.db"


def get_db_connection():
  conn = sqlite3.connect(DB_NAME)
  # Explicitly enable foreign key support in SQLite
  conn.execute("PRAGMA foreign_keys = ON;")
  return conn


def init_database():
  """Initializes the database schema and seeds sample entries if empty."""
  conn = get_db_connection()
  cursor = conn.cursor()

  # Create tables with relational constraints and cascading deletes
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS drilling_rigs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rig_name TEXT UNIQUE NOT NULL,
            contact_email TEXT NOT NULL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rig_id INTEGER NOT NULL,
            extraction_site TEXT NOT NULL,
            extraction_date TEXT NOT NULL,
            FOREIGN KEY (rig_id) REFERENCES drilling_rigs (id) ON DELETE CASCADE
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS fossil_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id INTEGER NOT NULL,
            analysis_type TEXT NOT NULL,
            measured_value REAL NOT NULL,
            FOREIGN KEY (sample_id) REFERENCES core_samples (id) ON DELETE CASCADE
        )
    """)

  # Check if tables are empty, and seed sample data if so
  cursor.execute("SELECT COUNT(*) FROM drilling_rigs")
  if cursor.fetchone()[0] == 0:
    # Seed Rigs
    cursor.execute(
        "INSERT INTO drilling_rigs (rig_name, contact_email)"
        " VALUES (?, ?)",
        ("T-Rex Digger Alpha", "alpha.rig@palaeotech.org"),
    )
    cursor.execute(
        "INSERT INTO drilling_rigs (rig_name, contact_email)"
        " VALUES (?, ?)",
        ("Stego Drill Beta", "beta.drills@palaeotech.org"),
    )

    # Seed Core Samples
    cursor.execute(
        "INSERT INTO core_samples (rig_id, extraction_site, extraction_date)"
        " VALUES (?, ?, ?)",
        (1, "Hell Creek Formation – Trench 4", "2026-03-12"),
    )
    cursor.execute(
        "INSERT INTO core_samples (rig_id, extraction_site, extraction_date)"
        " VALUES (?, ?, ?)",
        (2, "Morrison Basin – Trench 2", "2026-04-05"),
    )

    # Seed Fossil Analyses
    cursor.execute(
        "INSERT INTO fossil_analyses (sample_id, analysis_type, measured_value)"
        " VALUES (?, ?, ?)",
        (1, "Fossil Count", 14.0),
    )
    cursor.execute(
        "INSERT INTO fossil_analyses (sample_id, analysis_type, measured_value)"
        " VALUES (?, ?, ?)",
        (2, "Bone Fragment Mass (g)", 250.5),
    )

    conn.commit()

  conn.close()


class PalaeontologyApp:

  def __init__(self, root):
    self.root = root
    self.root.title(
        "Relational Palaeontology Drilling Rig & Core Sample Dashboard"
    )
    self.root.geometry("900x700")

    init_database()

    # Main Layout Containers
    # Top Section: Insert and Delete Panels side-by-side or stacked cleanly
    control_frame = ttk.Frame(self.root, padding=10)
    control_frame.pack(fill=tk.X, padx=10, pady=5)

    self.create_insert_panel(control_frame)
    self.create_delete_panel(control_frame)

    # Bottom Section: Tabbed Display Panel
    self.create_tabbed_display(self.root)

    # Initial data population
    self.refresh_all_views()

  def create_insert_panel(self, parent):
    frame = ttk.LabelFrame(parent, text=" Add New Record ", padding=10)
    frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    # Variables
    self.rig_name_var = tk.StringVar()
    self.email_var = tk.StringVar()
    self.site_var = tk.StringVar()
    self.date_var = tk.StringVar()
    self.analysis_type_var = tk.StringVar()
    self.value_var = tk.StringVar()

    fields = [
        ("Rig Name:", self.rig_name_var),
        ("Supervisor Email:", self.email_var),
        ("Extraction Site:", self.site_var),
        ("Extraction Date (YYYY-MM-DD):", self.date_var),
        ("Analysis Type:", self.analysis_type_var),
        ("Measured Value:", self.value_var),
    ]

    for idx, (label_text, var) in enumerate(fields):
      ttk.Label(frame, text=label_text).grid(
          row=idx, column=0, sticky=tk.W, pady=2
      )
      ttk.Entry(frame, textvariable=var, width=25).grid(
          row=idx, column=1, sticky=tk.W, pady=2
      )

    submit_btn = ttk.Button(
        frame, text="Add Record", command=self.handle_insert
    )
    submit_btn.grid(
        row=len(fields), column=0, columnspan=2, pady=10, sticky=tk.EW
    )

  def create_delete_panel(self, parent):
    frame = ttk.LabelFrame(parent, text=" Delete Management ", padding=10)
    frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    ttk.Label(frame, text="Select Target to Delete:").grid(
        row=0, column=0, sticky=tk.W, pady=2
    )

    self.delete_target_type = tk.StringVar(value="Rig")
    target_types = ["Rig", "Core Sample", "Fossil Analysis"]

    target_menu = ttk.Combobox(
        frame,
        textvariable=self.delete_target_type,
        values=target_types,
        state="readonly",
    )
    target_menu.grid(row=0, column=1, sticky=tk.W, pady=2)
    target_menu.bind("<<ComboboxSelected>>", self.update_delete_dropdown)

    ttk.Label(frame, text="Select Specific Item:").grid(
        row=1, column=0, sticky=tk.W, pady=2
    )

    self.delete_item_var = tk.StringVar()
    self.item_dropdown = ttk.Combobox(
        frame, textvariable=self.delete_item_var, state="readonly", width=30
    )
    self.item_dropdown.grid(row=1, column=1, sticky=tk.W, pady=2)

    delete_btn = ttk.Button(
        frame, text="Delete Selected", command=self.handle_delete
    )
    delete_btn.grid(
        row=2, column=0, columnspan=2, pady=15, sticky=tk.EW
    )

    self.update_delete_dropdown()

  def create_tabbed_display(self, parent):
    tab_frame = ttk.Frame(parent, padding=10)
    tab_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self.notebook = ttk.Notebook(tab_frame)
    self.notebook.pack(fill=tk.BOTH, expand=True)

    # Setup Tables/Tabs
    self.tab_join = ttk.Frame(self.notebook)
    self.tab_rigs = ttk.Frame(self.notebook)
    self.tab_samples = ttk.Frame(self.notebook)
    self.tab_analyses = ttk.Frame(self.notebook)

    self.notebook.add(self.tab_join, text="Tab 1: Combined JOIN View")
    self.notebook.add(self.tab_rigs, text="Tab 2: Drilling Rigs")
    self.notebook.add(self.tab_samples, text="Tab 3: Core Samples")
    self.notebook.add(self.tab_analyses, text="Tab 4: Fossil Analyses")

    # Treeview setup helpers
    self.tree_join = self.create_treeview(
        self.tab_join,
        (
            "Sample ID",
            "Rig Name",
            "Extraction Site",
            "Extraction Date",
            "Analysis Type",
            "Measured Value",
        ),
    )
    self.tree_rigs = self.create_treeview(
        self.tab_rigs, ("ID", "Rig Name", "Contact Email")
    )
    self.tree_samples = self.create_treeview(
        self.tab_samples, ("Sample ID", "Rig ID", "Extraction Site", "Date")
    )
    self.tree_analyses = self.create_treeview(
        self.tab_analyses, ("Analysis ID", "Sample ID", "Analysis Type", "Value")
    )

  def create_treeview(self, parent, columns):
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
      tree.heading(col, text=col)
      tree.column(col, width=120, anchor=tk.W)

    scrollbar = ttk.Scrollbar(
        frame, orient=tk.VERTICAL, command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    return tree

  def handle_insert(self):
    # Input Validation
    rig_name = self.rig_name_var.get().strip()
    email = self.email_var.get().strip()
    site = self.site_var.get().strip()
    date = self.date_var.get().strip()
    analysis_type = self.analysis_type_var.get().strip()
    val_str = self.value_var.get().strip()

    if not all([rig_name, email, site, date, analysis_type, val_str]):
      messagebox.showerror(
          "Validation Error", "All text fields must be filled out."
      )
      return

    try:
      measured_value = float(val_str)
      if measured_value < 0:
        raise ValueError("Measured value cannot be negative.")
    except ValueError as e:
      messagebox.showerror(
          "Validation Error",
          f"Invalid measured value. Please enter a valid non-negative"
          f" number.\nDetails: {e}",
      )
      return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
      # Logic check: If the rig already exists, use existing ID; else create new profile.
      cursor.execute(
          "SELECT id FROM drilling_rigs WHERE rig_name = ?", (rig_name,)
      )
      rig_row = cursor.fetchone()

      if rig_row:
        rig_id = rig_row[0]
        # Optionally update email if needed, or keep existing
      else:
        cursor.execute(
            "INSERT INTO drilling_rigs (rig_name, contact_email) VALUES (?,"
            " ?)",
            (rig_name, email),
        )
        rig_id = cursor.lastrowid

      # Create one new core sample extracted by that rig
      cursor.execute(
          "INSERT INTO core_samples (rig_id, extraction_site, extraction_date)"
          " VALUES (?, ?, ?)",
          (rig_id, site, date),
      )
      sample_id = cursor.lastrowid

      # Create one fossil analysis recorded under it
      cursor.execute(
          "INSERT INTO fossil_analyses (sample_id, analysis_type,"
          " measured_value) VALUES (?, ?, ?)",
          (sample_id, analysis_type, measured_value),
      )

      conn.commit()
      messagebox.showinfo(
          "Success", "New record inserted successfully with cascading link!"
      )

      # Clear out text variables instantly
      self.rig_name_var.set("")
      self.email_var.set("")
      self.site_var.set("")
      self.date_var.set("")
      self.analysis_type_var.set("")
      self.value_var.set("")

      self.refresh_all_views()

    except Exception as e:
      conn.rollback()
      messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
      conn.close()

  def update_delete_dropdown(self, event=None):
    target_type = self.delete_target_type.get()
    conn = get_db_connection()
    cursor = conn.cursor()

    items = []
    if target_type == "Rig":
      cursor.execute("SELECT id, rig_name FROM drilling_rigs")
      items = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
    elif target_type == "Core Sample":
      cursor.execute(
          "SELECT cs.id, dr.rig_name, cs.extraction_site FROM core_samples cs"
          " JOIN drilling_rigs dr ON cs.rig_id = dr.id"
      )
      items = [
          f"{row[0]} (Rig: {row[1]}, Site: {row[2]})" for row in cursor.fetchall()
      ]
    elif target_type == "Fossil Analysis":
      cursor.execute(
          "SELECT fa.id, fa.analysis_type, fa.measured_value, cs.id FROM"
          " fossil_analyses fa JOIN core_samples cs ON fa.sample_id = cs.id"
      )
      items = [
          f"{row[0]}: {row[1]} = {row[2]} (Sample ID: {row[3]})"
          for row in cursor.fetchall()
      ]

    conn.close()

    self.item_dropdown["values"] = items
    if items:
      self.item_dropdown.current(0)
    else:
      self.delete_item_var.set("")

  def handle_delete(self):
    selected_item_str = self.delete_item_var.get()
    if not selected_item_str:
      messagebox.showerror(
          "Selection Error", "No item selected for deletion."
      )
      return

    # Extract ID from the string representation (assumes ID is at the very beginning before ':')
    try:
      item_id = int(selected_item_str.split(":")[0].split(" ")[0])
    except ValueError:
      messagebox.showerror("Error", "Could not parse the selected item ID.")
      return

    target_type = self.delete_target_type.get()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
      if target_type == "Rig":
        # Cascading delete will wipe out associated core samples and fossil analyses
        cursor.execute("DELETE FROM drilling_rigs WHERE id = ?", (item_id,))
      elif target_type == "Core Sample":
        # Cascading delete will wipe out associated fossil analyses
        cursor.execute("DELETE FROM core_samples WHERE id = ?", (item_id,))
      elif target_type == "Fossil Analysis":
        # Deleting a Fossil Analysis removes only that row (parent records remain intact)
        cursor.execute("DELETE FROM fossil_analyses WHERE id = ?", (item_id,))

      conn.commit()
      messagebox.showinfo("Success", f"Deleted selected {target_type} successfully.")

      self.refresh_all_views()

    except Exception as e:
      conn.rollback()
      messagebox.showerror("Database Error", f"Deletion failed: {e}")
    finally:
      conn.close()

  def refresh_all_views(self):
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Tab 1: JOIN View ---
    for row in self.tree_join.get_children():
      self.tree_join.delete(row)

    cursor.execute("""
            SELECT cs.id, dr.rig_name, cs.extraction_site, cs.extraction_date, 
                   fa.analysis_type, fa.measured_value
            FROM fossil_analyses fa
            JOIN core_samples cs ON fa.sample_id = cs.id
            JOIN drilling_rigs dr ON cs.rig_id = dr.id
        """)
    for row in cursor.fetchall():
      self.tree_join.insert("", tk.END, values=row)

    # --- Tab 2: Drilling Rigs ---
    for row in self.tree_rigs.get_children():
      self.tree_rigs.delete(row)
    cursor.execute("SELECT id, rig_name, contact_email FROM drilling_rigs")
    for row in cursor.fetchall():
      self.tree_rigs.insert("", tk.END, values=row)

    # --- Tab 3: Core Samples ---
    for row in self.tree_samples.get_children():
      self.tree_samples.delete(row)
    cursor.execute("SELECT id, rig_id, extraction_site, extraction_date FROM core_samples")
    for row in cursor.fetchall():
      self.tree_samples.insert("", tk.END, values=row)

    # --- Tab 4: Fossil Analyses ---
    for row in self.tree_analyses.get_children():
      self.tree_analyses.delete(row)
    cursor.execute("SELECT id, sample_id, analysis_type, measured_value FROM fossil_analyses")
    for row in cursor.fetchall():
      self.tree_analyses.insert("", tk.END, values=row)

    conn.close()

    # Update Delete Panel dropdown lists so deleted items are removed
    self.update_delete_dropdown()


if __name__ == "__main__":
  root = tk.Tk()
  app = PalaeontologyApp(root)
  root.mainloop()