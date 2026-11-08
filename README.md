# Relational Palaeontology Drilling Rig & Core Sample Analysis Dashboard

A desktop application built in Python using **Tkinter** and **SQLite3** designed to manage drilling operations, core sample cataloging, and fossil analyses for palaeontology research institutes. 

This project replaces traditional, error-prone spreadsheets with a normalized relational database architecture that enforces strict data integrity constraints, cascading deletions, and real-time user interface updates.

---

## Key Features

* **Relational Database Integrity:** Built on SQLite3 with explicit foreign key enforcement (`PRAGMA foreign_keys = ON;`).
* **Automated Cascade Deletions:** Configured with `ON DELETE CASCADE` rules:
  * Deleting a **Drilling Rig** automatically deletes all linked core samples and their associated fossil analyses.
  * Deleting a **Core Sample** automatically deletes all associated fossil analyses.
  * Deleting a **Fossil Analysis** removes only that specific record, leaving parent entities intact.
* **Intelligent Insert Panel:** 
  * Automatically reuses existing Rig IDs when an existing rig name is entered.
  * Automatically creates a new rig profile when a new name is entered.
  * Links every submission to one core sample and one corresponding fossil analysis record.
* **Input Validation & Safety:** Prevents empty text submissions and rejects negative or non-numeric values for measurements.
* **Dynamic Delete Panel:** Real-time dropdown selection lists that clear deleted entries automatically to prevent orphaned selection states.
* **4-Tab Real-Time Dashboard View:**
  * **Tab 1:** Multi-table `JOIN` view consolidating Sample ID, Rig Name, Extraction Site, Extraction Date, Analysis Type, and Measured Value.
  * **Tabs 2, 3, & 4:** Raw, standalone views of the backend database tables (`drilling_rigs`, `core_samples`, and `fossil_analyses`).

---

## Architecture & Database Schema

The database consists of three relational tables:

1. `drilling_rigs`
   * `id` (INTEGER, Primary Key, Auto-Increment)
   * `rig_name` (TEXT, Unique)
   * `contact_email` (TEXT)

2. `core_samples`
   * `id` (INTEGER, Primary Key, Auto-Increment)
   * `rig_id` (INTEGER, Foreign Key → `drilling_rigs(id)` ON DELETE CASCADE)
   * `extraction_site` (TEXT)
   * `extraction_date` (TEXT)

3. `fossil_analyses`
   * `id` (INTEGER, Primary Key, Auto-Increment)
   * `sample_id` (INTEGER, Foreign Key → `core_samples(id)` ON DELETE CASCADE)
   * `analysis_type` (TEXT)
   * `measured_value` (REAL)

---

## Installation & Running

### Prerequisites
* Python 3.x
* Tkinter and SQLite3 (included standard with Python desktop distributions)

### Execution
1. Clone this repository:
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/palaeontology-dashboard.git](https://github.com/YOUR_GITHUB_USERNAME/palaeontology-dashboard.git)
   cd palaeontology-dashboard
