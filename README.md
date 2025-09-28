# The Daily Protocol Operator

The Daily Protocol Operator is a Telegram bot designed to help you build daily routines, set and achieve goals, and maintain healthy habits through interactive checklists and streak tracking. The bot is especially tailored for personal use and accountability, supporting daily streaks and statistics visualization.

## Features

- **Morning Routine**: Start your day with a checklist of healthy habits (e.g., shower, hydration, blocking social media, running).
- **Daily Goals**: Enter three custom goals every morning and track their completion.
- **Evening Review**: Complete an end-of-day checklist to reflect and close your day.
- **Streak Tracking**: Track your current and total streaks, and visualize them with a calendar image.
- **Accountability**: If goals are not completed, the bot notifies you and calculates a "penalty" for missed tasks.
- **Scheduling**: Automatic reminders for morning routines and end-of-day reviews.
- **Data Persistence**: All user data is stored locally in `user_data.json`.
- **Rich Telegram UI**: Uses inline buttons, message edits, and images for interaction.
- **Testing Utilities**: Includes commands to simulate routines and test all features.

## Installation

### Prerequisites

- Python 3.8+
- Telegram account & bot token (create via [@BotFather](https://core.telegram.org/bots#6-botfather))
- Fonts: `arial.ttf` or system equivalent for streak calendar (fallbacks are provided)
- (Optional) [Cold Turkey](https://getcoldturkey.com/) or similar app for social media blocking

### Required Python Packages

Install dependencies with:

```bash
pip install pyTelegramBotAPI schedule pytz pillow
```

## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/abdurakhmonoff/the-daily-protocol-bot.git
   cd the-daily-protocol-bot
   ```

2. **Configure Bot Token:**
   - Replace the `BOT_TOKEN` value in `main.py` with your own token from BotFather.

3. **Run the Bot:**
   ```bash
   python main.py
   ```

4. **Start Using:**
   - In Telegram, search for your bot and type `/help` to see available commands.

## Main Commands

- `/help` — Show all available commands and usage instructions
- `/test_morning` — Simulate the morning routine checklist
- `/test_goals` — Test the daily goals entry prompt
- `/test_evening` — Simulate the evening checklist
- `/test_completion` — Simulate completion of all tasks and see the streak image
- `/test_deadline` — Simulate missing goals to see penalty notification
- `/test_reset` — Reset all tasks for the day
- `/status` — Get a summary of your current routine/goal status and statistics
- `/test_streak` — Show detailed streak information
- `/test_image` — Generate and preview the streak calendar image
- `/set_chat` — Set the current chat as the primary chat for notifications
- `/debug` — Show debug info, including raw user data

## How It Works

### Daily Flow

1. **Morning (6:00 AM):**  
   - Bot sends you a checklist of morning tasks.  
   - Mark tasks as complete using inline buttons.

2. **After Morning Tasks:**  
   - Enter three custom goals for the day by replying in the specified format.

3. **Goal Tracking:**  
   - Mark each goal complete via inline buttons.

4. **Evening Review:**  
   - Once all goals are complete, the bot sends an evening checklist.

5. **Completion and Streak:**  
   - When all is done, the bot updates your streak, generates a monthly calendar image, and sends your statistics.

6. **Penalty/Accountability:**  
   - At 23:59, if daily goals are not complete, the bot lists uncompleted goals and reminds you to make a charitable penalty.

### Data and Persistence

- User progress is stored in `user_data.json`.
- Streaks and completions are visualized using a generated PNG calendar (`streak_calendar.png`).

### Scheduling

- Uses the `schedule` library to trigger routines/reminders at 06:00 and 23:59 Tashkent time.
- Scheduler runs in a separate thread to support both scheduled tasks and Telegram polling.

## Data Structure (user_data.json)

```json
{
  "morning_tasks": [false, false, false],
  "daily_goals": [],
  "daily_goals_status": [false, false, false],
  "evening_tasks": [false, false, false],
  "current_streak": 0,
  "total_streak": 0,
  "last_completion_date": null,
  "monthly_completions": {
    "2025-09": [1, 2, 3, ...]
  }
}
```

## Customization

- **Routine Tasks:** Edit lists under `send_morning_routine` and `send_evening_checklist` functions.
- **Timezone:** Change `TIMEZONE` in `main.py` for your local time.
- **Penalty/Accountability:** Change `FATHER_USERNAME` and penalty messages as needed.

## Security Note

**Do NOT commit your real bot token to public repositories!**  
The example token in `main.py` is for illustration. Always keep your token secret.

## License

MIT License.

---

**Created by [@abdurakhmonoff](https://github.com/abdurakhmonoff)**
