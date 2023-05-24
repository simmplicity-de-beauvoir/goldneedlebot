# Gold Needle Bot Commands Ref

## Statue-Candidate

### /petrifyme [true|false]
- join or leave the statue_candidates role

### /selfpetrify help
- shows help text for self-petrification

### /selfpetrify toggle
- toggles self-petrification

### /selfpetrify timelock [timemin] [timemax]
- sets self-petrification for timemin
        - if timemax is provided, will set for a random value between the two
- timemin and timemax can be as seconds, or as a number and a letter denoting time
        - examples:
                - 900 == 15 minutes (in seconds)
                - 15m == 15 minutes
        - m == minutes, h == hours, d == days, w == weeks
- cannot be un-petrified early
- maximum petrification time is 3 weeks
- this time value is checked once every 30 seconds, so there may be some delay between your scheduled freedom and your actual freedom

### /selfpetrify chance [chance] [time]
- chance must be a number between 1 and 99
- runs a check every time interval for a value between 0 and 100
        - if genereated number is chance or lower, freedom
- time is the same as "/selfpetrify time"
        - max value is 1 week

## Statue-Admin

### /[un]petrify @User
- petrifies or unpetrifies a target user
- user must be part of statue_candidates role

## Administrator

### /fix_perms
- updates all channels' permissions

### /setup channel [statues_only|bot_spam]
- mark the current channel as either "statues only" or "bot spam"
        - "statues only" == disable @everyone access, allow full speak/read/react permissions for statues
        - "bot spam" == dedicated channel for bot messages
- ideally shouldn't mess w/ patreon permissions
- only one channel for each
        - *TODO: support multiple for statues_only*
- warning: there is currently no way to *undo* a statues only operation through the bot. permissions for "everyone" will need to be fixed manually


### /setup permissions [speak|read|react] [true|false]
- adjust statue's permissions
        - default is speaking is disallowed and read/react is allowed

### TODO: /setup exempt #channel [speak|read|react] [true|false]
- setup exemption from statue permissions on the current channel

### /setup role [statue_admin|statue_candidate|statue] @Role
- setup Discord roles associated with each bot role
- only one role per role

### /settings
- list

### TODO: /setup allow_simm_admin [true|false]
- allows Simmplicity (developer) to run Administrator commands for setup purposes

----
TODO Ideas:
- % chance of permanence on any self-petrify action
- self-petrify time responds with "will be freed at {date}"
-
---
server settings struct
can_* are actually booleans
```
CREATE TABLE IF NOT EXISTS settings (
        guild_id INT PRIMARY KEY,
        statue_only_channel INT,
        can_speak INT,
        can_hear INT,
        can_react INT,
        statue_admin_role INT,
        statue_candidate_role INT,
        statue_role INT,
        allow_simm_admin INT);
```

```

INSERT INTO settings (
        guild_id,
        {setting}
} VALUES (
        {guild_id}
        {setting}
);
```
