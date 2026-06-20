# Project Handover Context for Antigravity (Windows)

**Hello! If you are reading this, you are the Antigravity instance running on the user's Windows PC.** 
I am the Antigravity instance from the user's Mac. I have compiled this handover document so you have the exact context of what we achieved today, and what your mission is moving forward.

## Project Goal
The user wants to automatically extract patient test results from their **Horiba Yumizen CA60** analyzer and push them to their **Flabs LIS** cloud account, without relying on legacy RS-232 serial cables.

## What We Discovered
1. **The Machine (Horiba CA60):** We discovered it runs a modern HTTP server on `http://192.168.1.3:8080`. We successfully bypassed legacy ASTM protocols and pulled raw JSON data from it by sending a `POST` request to `/queries` with a GraphQL-style payload.
2. **The Poller Script:** We wrote a Python script (`horiba_watcher.py`) that successfully polls the machine every 10 seconds. It memorizes existing Sample IDs, and when a new test finishes, it successfully detects it and parses the Test Name and Result.
3. **The Target (Flabs LIS):** We inspected the Flabs local desktop agent running on the user's Windows PC (`http://localhost:4000`). It is a mapping dashboard. Unfortunately, we found no evidence that it supports "Folder Sync" or "CSV Import". However, we noted a "Create Tables" button, strongly implying it stores its data in a local hidden database (like SQLite, Access, or local SQL Server) before syncing to the cloud.

## Your Mission on Windows (Next Steps)
The user has decided to pursue a "hacker route" to finish this integration locally on Windows while they wait for official vendor support.

Your objective is to modify our `horiba_watcher.py` script so that it writes the data directly into the Flabs local database.

**Step-by-step tasks:**
1. **Locate the Flabs Database:** Ask the user where the Flabs uploading software is installed (likely in `C:\Program Files` or `C:\ProgramData` or `%AppData%`). Use your tools to search that directory for local database files (look for `.sqlite`, `.db`, `.mdb`, or similar).
2. **Reverse Engineer the Schema:** Open the database file you found and examine its tables. Find the table where the "Mapped Tests" or "Pending Uploads" are stored.
3. **Update the Python Script:** Modify the `horiba_watcher.py` script (which is in this repository). Currently, it just `print()`s the new results to the terminal. You need to add a function that takes the `sample_id`, `test_name`, and `result` and executes an `INSERT` statement directly into the Flabs database table you discovered.
4. **Test the Sync:** Once the Python script inserts a row, have the user check the Flabs Cloud Dashboard to confirm the local agent successfully picked it up and synced it to the cloud!

Good luck! You have all the tools necessary to finish this integration natively on the Windows machine.
