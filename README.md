# Mini-EDC (Electronic Data Capture System)

A lightweight Django-based system for managing clinical trial data.  
Built as a learning/demo project inspired by the real EDC platform at Rigshospitalet (INCEPT).

---

## 🌍 Overview

This app simulates how modern clinical trials collect and organize data.  
It lets researchers:

- Define **Studies** (e.g., a clinical trial).
- Enroll **Subjects** (patients) into a study.
- Record **Visits** for each subject (Baseline, Follow-up, etc.).
- Capture **Adverse Events** (side effects, complications).
- Build **CRFs** (Case Report Forms) to define what fields must be collected at each visit.

The goal is to provide a structured, web-based data capture workflow for research teams.

---

## 🗂️ Core Data Model

- **Study** → Top-level container (trial or research project).  
- **Subject** → A patient enrolled in a specific study.  
- **Visit** → A scheduled/unscheduled patient encounter.  
- **Adverse Event** → An issue reported for a subject (e.g., fever, infection).  
- **CRF (Case Report Form)** → Defines what fields must be collected at visits.

Relationships:

- A `Study` has many `Subjects`.  
- A `Subject` has many `Visits` and `Adverse Events`.  
- Each `Visit` may have CRF entries.

---

## ⚡ Features

- Web dashboard (Studies → Subjects → Visits).  
- Adverse events can be added dynamically via **htmx** (no full page reload).  
- Case Report Form (CRF) builder with support for choice fields.  
- Admin interface for managing studies, subjects, visits, and CRFs.  
- PostgreSQL + container support (via Podman/Docker).  
- CI pipeline with GitHub Actions (SQLite + Postgres tests, image build & push).  
- Ready-to-run with a single `make` command.

---

## 🚀 Quickstart (Local)

### 1. Clone the repo

```bash
git clone https://github.com/IoannisTselios/mini-edc.git
cd mini-edc
