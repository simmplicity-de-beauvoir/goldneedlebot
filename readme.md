# Gold Needle Bot (name is WIP)
A Discord RP bot with teeth. 

## Usage (User)
There are three primary commands for users. All three are supported as slash commands or with the `--` prefix (so `--selfpetrify`).
- `/iwanttobepetrified`
	- Will sign you up for the statue-candidate role so that admins can petrify/unpetrify you. 
	- If petrified by an admin, only an admin can unpetrify you.
- `/selfpetrify toggle`
	- Will switch you between being petrified and not being a petrified. Assuming you aren't petrified for another reason, you can un-petrify yourself at any time.
- `/selfpetrify timelock <val1> [val2]`
	- Will petrify you for `val1` amount of time, or a random value between `val1` and `val2` if you provide both.
	- Values take the format of seconds, or a number with a letter suffix (`20` is 20 seconds, `20d` is 20 days)
	- `m` for minutes, `h` for hours, `d` for days, `w` for weeks
	- The maximum time is 4 weeks.
	- If using the slash command version, make sure you put the second value in the timemax parameter and not with a space. 

## Server Setup
- There must be the following roles:
	- An "admin" role for those allowed to petrify others.
	- A "petrification candidate" role for those who can be petrified.
	- A "active statue" role for those who *are* petrified.

## Inspirations
- DiscordFateBot by FailedSave
	- The FailedSave's bot 
- Project Avatar AKA the Avatar Charm by Sarah Passerine
	- Inspired the "statue only chat"

## Credits
- **Simmplicity**: Bot code
<span style="display:none;">
- **AlterKyon**: Art assets
- **Gargorgeous**: Dialogue
- **Statue Cafe Discord Server**: Moral support
</span>
