# HOST.md — fill this in BEFORE deploying (Phase 0 of BUILD_PLAN.md)

Answer every question and commit the answers. If "two Passenger apps on one
account" is a no, the whole layout changes — find out now.

| Question | Answer |
|---|---|
| Python version offered by cPanel | _TODO_ |
| Node version offered by cPanel | _TODO_ |
| MySQL 8 / MariaDB 10.6+ available? | _TODO_ |
| Cron minimum interval | _TODO_ |
| **Total memory cap** | _TODO_ |
| `nproc` / entry-process cap | _TODO_ |
| CPU-second limits | _TODO_ |
| **Inode limit** | _TODO_ |
| SSH access? | _TODO_ |
| Two Passenger apps on one account? | _TODO_ |

Day-3 smoke test: run both apps, `ab -n 500 -c 10` against the frontend, watch
cPanel's resource graph. If Node OOMs at 10 concurrent, that is the real
constraint — better to learn it now than on launch day.
