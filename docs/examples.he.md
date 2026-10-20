# דוגמאות

## שירותים

כל השירותים נמצאים תחת `dud_shemesh.` ומקבלים `entry_id` כפרמטר רשות (ראו [כמה דודים](features.md#multiple-water-heaters)).

| שירות | מטרה |
| ----- | ---- |
| `dud_shemesh.boost` | הפעלת הדוד ל-N דקות (`minutes`, בין 1 ל-720, ברירת מחדל 60). |
| `dud_shemesh.cancel_boost` | כיבוי הדוד מיד. |
| `dud_shemesh.set_mode` | `auto`, `schedule` או `off`. |
| `dud_shemesh.set_target_temp` | שינוי הטמפרטורה הרצויה (`temp`, בין 20 ל-80 מעלות). |
| `dud_shemesh.add_schedule` | הוספת לוח זמנים קבוע. מחזיר את המזהה החדש. |
| `dud_shemesh.update_schedule` | עדכון לוח זמנים לפי `schedule_id`. |
| `dud_shemesh.remove_schedule` | מחיקת לוח זמנים לפי `schedule_id`. |
| `dud_shemesh.legionella_run_now` | הפעלת מחזור חימום של 60 מעלות ומעלה. |
| `dud_shemesh.list_config` | מחזיר לוחות זמנים, היסטוריה, הפעלה פעילה, אפשרויות ומצב נוכחי (שירות עם תגובה). |

### הפעלה מהירה ל-45 דקות

```yaml
action: dud_shemesh.boost
data:
  minutes: 45
```

### לוח זמנים לבוקר, בימים א' עד ה'

```yaml
action: dud_shemesh.add_schedule
data:
  name: Morning shower
  time: "06:00"
  days: [sun, mon, tue, wed, thu]
  duration_minutes: 60
  target_temp: 55
```

הערכים של `days` הם `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`. הפרמטר `target_temp` הוא רשות; כשהוא מוגדר, ההפעלה מדולגת אם המים כבר חמים.

### דילוג חד-פעמי על ההפעלה הבאה

`skip_until` הוא חותמת זמן של Unix. הפעלות שהיו אמורות להתחיל לפניה מדולגות. `0` מבטל את הדילוג.

```yaml
action: dud_shemesh.update_schedule
data:
  schedule_id: "abc123"
  skip_until: 1790000000
```

### קריאת כל ההגדרות

```yaml
action: dud_shemesh.list_config
response_variable: dud
```

## אירועים

| אירוע | מתי | נתונים |
| ----- | --- | ------ |
| `dud_shemesh_heat_started` | הדוד הודלק | `source`, `duration_min`, `target_temp`, `starting_temp` |
| `dud_shemesh_heat_finished` | הדוד כובה | `source`, `status`, `duration_min` (מתוכנן), `actual_min` (זמן פעולה בפועל), `starting_temp`, `ending_temp` |
| `dud_shemesh_target_reached` | המיכל הגיע ליעד במהלך חימום | `source`, `temp`, `target_temp` |

הערכים של `status` הם `completed`, `target_reached`, `cancelled`, `manual_stop`, `external_stop`, `superseded`, `voice`, `expired_during_downtime`.

הקוד שולח גם את האירועים `dud_shemesh_heat_not_rising`, `dud_shemesh_boost_extended` ו-`dud_shemesh_auto_preheat_planned`.

### הודעה שהמים חמים

```yaml
alias: Hot water ready
triggers:
  - trigger: event
    event_type: dud_shemesh_target_reached
actions:
  - action: notify.notify
    data:
      message: "The water heater reached {{ trigger.event.data.temp }} °C"
```

### רישום של כל הפעלה שהסתיימה

```yaml
triggers:
  - trigger: event
    event_type: dud_shemesh_heat_finished
actions:
  - action: logbook.log
    data:
      name: Dud Shemesh
      message: >
        {{ trigger.event.data.status }}, {{ trigger.event.data.actual_min }} min,
        {{ trigger.event.data.starting_temp }} to {{ trigger.event.data.ending_temp }} °C
```

## שליטה בקול (Assist) {#voice-assist}

האינטגרציה רושמת את הפקודות `DudShemeshBoost`, `DudShemeshStop` ו-`DudShemeshStatus`. כדי להשתמש בהן, מעתיקים את קובץ המשפטים של השפה ומפעילים מחדש את Home Assistant:

| שפה | קובץ במאגר | להעתיק אל |
| --- | ---------- | --------- |
| אנגלית | [`docs/assist/en/dud_shemesh.yaml`](https://github.com/bareli/dud_shemesh/blob/main/docs/assist/en/dud_shemesh.yaml) | `<config>/custom_sentences/en/dud_shemesh.yaml` |
| עברית | [`docs/assist/he/dud_shemesh.yaml`](https://github.com/bareli/dud_shemesh/blob/main/docs/assist/he/dud_shemesh.yaml) | `<config>/custom_sentences/he/dud_shemesh.yaml` |

דוגמאות: "תדליק את הדוד לחצי שעה", "יש מים חמים", "תכבה את הדוד". הישות `water_heater` עובדת גם עם פקודות ההדלקה והכיבוי המובנות.

## לוח Energy

הוסיפו את חיישן **האנרגיה** של הדוד כמכשיר בודד בלוח **הגדרות ← לוחות מחוונים ← Energy**. זהו מונה קוט״ש מצטבר (`total_increasing`).
