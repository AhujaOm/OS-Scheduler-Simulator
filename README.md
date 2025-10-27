# 🧩 OS-Scheduler-Simulator  
An interactive CPU scheduling simulator that visualizes process scheduling algorithms in real-time.  

---

## 🧠 Overview  
**OS-Scheduler-Simulator** is a Python-based project that simulates and compares various CPU scheduling algorithms.  
It offers a clear, visual understanding of how different scheduling strategies affect process execution, waiting time, and turnaround time — making it ideal for Operating Systems coursework and research.  

Developed collaboratively by a team to combine theory with practical implementation.  

---

## ⚙️ Algorithms Implemented  
- **FCFS (First Come First Serve)**  
- **SJF (Shortest Job First)**  
- **Priority Scheduling**  
- **Round Robin Scheduling**  

Each algorithm demonstrates process order, Gantt chart visualization, and performance metrics.  

---

## 💡 Key Features  
- **Visual Execution Flow** – Observe how each process gets scheduled and completed.  
-  **Comparative Metrics** – Displays average waiting and turnaround times.  
-  **Intuitive Input System** – Enter burst time, priority, and arrival time easily.  
-  **Dynamic Visualization** – Simulates CPU context switching step-by-step.  
-  **Educational Focus** – Designed to strengthen OS and scheduling fundamentals.  

---

## 🔧 Prerequisites  
- **Python Version:** python3  
- Supported Platforms: Windows, macOS, Linux  
- Required Library:  
  ```bash
  pip install matplotlib
  ```

---

## 🚀 Setup & Execution  
1. **Clone the Repository**  
   ```bash
   git clone https://github.com/AhujaOm/OS-Scheduler-Simulator.git
   cd OS-Scheduler-Simulator
   ```  

2. **Run the Simulator**  
   ```bash
   python main.py
   ```  

3. **Follow the Prompts**  
   Enter process details and select your desired scheduling algorithm.  

---

## 🧮 Example Output  
Running **Round Robin Scheduling**  

```
Enter number of processes: 3
Enter time quantum: 4

Gantt Chart:
| P1 | P2 | P3 | P2 | P3 |

Average Waiting Time: 6.33
Average Turnaround Time: 12.67
```

---

## 🤝 Contributors  
| Name | GitHub Username |
|------|-----------------|
| **Om Ahuja** | [AhujaOm](https://github.com/AhujaOm) |
| **Rikin Parekh** | [RikinParekh15147](https://github.com/RikinParekh15147) |
| **Mit Darji** | [mitkdarji](https://github.com/mitkdarji) |

---
