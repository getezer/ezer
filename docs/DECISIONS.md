# Ezer - Learning Journal
## Badal Satapathy | Started April 2026

This file documents what I learn each day while building Ezer.
Written in my own words. For my own growth.
Also visible on GitHub as evidence of a builder who reflects.

---

## Day 1 - April 15, 2026
### Environment Setup

**What we built:**
Set up the entire development environment on a fresh MacBook Air.
By end of day, code was live on github.com/getezer/ezer.

**What I learned:**

**Homebrew** - The App Store for developer tools on Mac.
Everything else gets installed through this one tool.

**Python** - The language the Ezer backend is written in.
Version 3.11 specifically - always use a specific version, not the latest,
because libraries need time to catch up with new versions.

**Node.js** - The engine that runs React, our frontend framework.
We do not write Node.js code directly. It just needs to be running.

**VS Code** - The workbench where all Ezer code is written and read.
Like Microsoft Word but for code. Free. Used by millions of developers.

**Git and GitHub** - Git takes snapshots of your work locally.
GitHub stores those snapshots online. Together they mean your work
is never lost and always visible to the world as your portfolio.

**Virtual environment (venv)** - A private isolated box for Ezer's
Python tools. Keeps Ezer's dependencies separate from everything
else on my Mac. Named venv by convention - every developer knows
what it means.

**Terminal** - An application on Mac that lets you give direct
instructions to your computer by typing commands. The language
is called zsh. Commands look cryptic but each one does one specific
thing. Unix commands have weird names because they were named by
engineers in the 1970s who valued brevity over clarity.

**Key insight from Day 1:**
A website has two parts - frontend (what the user sees, built with React)
and backend (where the work happens, built with Python and FastAPI).
Like a restaurant - the dining room and the kitchen.

---

## Day 2 - April 16, 2026
### PDF Extraction and Rejection Analysis

**What we built:**
The brain of Ezer. Two engines that together read a denial letter
and understand it legally.

Engine 1 - PDF Extractor: Reads a denial letter PDF and pulls out
insurer name, policy number, CCN, rejection reason, date, hospital,
patient name, and denial type.

Engine 2 - Rejection Analyser: Takes the extracted fields and
assesses contestability, explains what the insurer is claiming
in plain English, generates legally grounded contestation language,
identifies structural impact, and recommends next steps.

Both tested on my father's real HDFC ERGO denial letters.
Both returned HIGH contestability with correct legal grounding.

**What I learned:**

**FastAPI** - A Python framework for building backends.
A framework is like a pre-built kitchen - counters, stove, sink
already there. You bring the ingredients and cook.
FastAPI handles file uploads, responses, and error handling.
You write the business logic.

**API vs local function** - A local function runs on your own
computer in microseconds. An API call sends a message over the
internet to someone else's computer and waits for a response.
Seconds not microseconds. Costs money. Can fail.

**JSON** - The universal language of web communication.
Not a file format we create. Just structured text that travels
between systems. The user decides whether to save it as a file.
Curly brackets, key-value pairs, readable by any programming language.

**Process and Discard** - Ezer's privacy principle from the PRD.
We use temporary files that are automatically deleted after processing.
Nothing is stored on our server. The user owns their data.
This is both a legal compliance decision and a trust differentiator.

**SSH keys** - A permanent secure connection between my Mac and GitHub.
Like a key card that never expires and never needs a password.
Private key stays on my Mac. Public key goes to GitHub.
Set up once. Works forever.

**API key security** - An API key is like a hotel key card.
It proves you are a paying guest. Never share it. Never put it
in code. Always store in .env file. If exposed, delete and replace immediately.

**Key insight from Day 2:**
The API response is just a message. Like a WhatsApp message.
Who decides what to do with it after it arrives - store it,
display it, forward it, ignore it - is entirely the developer's decision.
This is what software architecture actually is. Not writing code.
Making decisions about how information flows.

**Personal note:**
Asked what I thought were basic questions about APIs, JSON, and
function returns. Realised these are actually architecture questions.
The systems thinking from 23 years of operations work is directly
applicable to software design. The vocabulary is different.
The thinking is the same.

---