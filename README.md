# Tasks of Glory

A lightweight Tkinter task manager that helps you choose what to do next by balancing **Ease** (how quick/simple) against **Urgency** (how time-sensitive). 
Drag to rank Ease or Urgency, and let the app compute a **Priority** score (`ease ÷ urgency`) so high-urgency items bubble up without ignoring easy wins.

## Features
- Add, check off, and double-click to edit tasks  
- Rank by **Ease** or **Urgency** (drag handle shows for the active column)  
- Auto-computed **Priority**; one-click “Sort by Priority”  
- Persisted to `tasks.txt` in the app folder

## Quick start
```bash
python Tasks.of.Glory.py
