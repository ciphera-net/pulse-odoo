#!/usr/bin/env bash
# Installs a real Odoo, activates this module, and reads the tag out of a
# served public page.
#
# 🔴 NOT RUN as part of building this module. This repository's own task
# forbids Docker ("the Docker VM is shared and small; real-install
# verification happens later, one platform at a time") — this script is that
# later, dedicated pass. Read it before running it; it records in comments
# exactly what it assumes versus what it asserts, and the things this
# repository could not verify without Odoo installed (see README.md's note on
# the exact bytes of the `defer` attribute, and tests/test_pulse_analytics.py's
# module docstring for the general shape of that gap).
#
#   ./scripts/verify.sh              # odoo:20.0 against postgres:16 by default
#   ODOO_IMAGE=odoo:20.0 ./scripts/verify.sh
#   ./scripts/verify.sh --mutate     # also proves every assertion can go red
#
# Every container, volume and network this script creates is named
# pulse-verify-odoo-<something>. Teardown removes ONLY resources matching that
# prefix, by exact name — never `docker system prune` or any other blanket
# cleanup, so it never touches another session's Docker resources.
#
# Needs: docker, curl. Nothing else — Odoo and Postgres run in containers.

set -uo pipefail

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODULE_SRC="$MODULE_DIR/pulse_analytics"

ODOO_IMAGE="${ODOO_IMAGE:-odoo:20.0}"
POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres:16}"
HTTP_PORT="${HTTP_PORT:-18069}"
PREFIX="pulse-verify-odoo"
NET="${PREFIX}-net"
DB_CONTAINER="${PREFIX}-db"
DB_VOLUME="${PREFIX}-db-data"
APP_CONTAINER="${PREFIX}-app"
WORK="${PULSE_ODOO_WORK:-${TMPDIR:-/tmp}/${PREFIX}-work}"
# Generated, not hard-coded. This Postgres is reachable only on the
# pulse-verify-odoo-net Docker network this script creates and tears down —
# nobody ever logs into it — but a literal password in a public repository is
# a thing somebody eventually reuses (same reasoning as pulse-joomla's
# scripts/verify.sh).
DB_PASSWORD="fixture-$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 24)"

MUTATE=0
[ "${1:-}" = "--mutate" ] && MUTATE=1

for tool in docker curl; do
  command -v "$tool" >/dev/null || { echo "REFUSING: $tool is not on PATH"; exit 1; }
done
docker info >/dev/null 2>&1 || { echo "REFUSING: docker is not usable (daemon not running?)"; exit 1; }

FAILURES=0
SCRIPT_URL='https://js\.ciphera\.net/script\.js'
# Matches this module's one script element wherever it appears, tolerant of
# attribute order and either boolean-attribute spelling — the SOURCE XML has
# no opinion on byte order, and neither should this check (see the Joomla
# README: "Attribute order is not meaningful in HTML — it is the same tag.").
TAG_PATTERN="<script[^>]*src=\"${SCRIPT_URL}\"[^>]*></script>"

# ── Cleanup: only our own named resources, by exact name ────────────────────
# Every name this script could possibly have created, listed once here, so
# the trap never needs reassigning later and a container left over from a
# crashed previous run is swept up too (docker rm -f on a name that does not
# exist just fails quietly, hence `|| true`).
cleanup() {
  docker rm -f \
    "$APP_CONTAINER" "${APP_CONTAINER}-control" \
    "${APP_CONTAINER}-init" "${APP_CONTAINER}-control-init" "${APP_CONTAINER}-mutant-init" \
    "$DB_CONTAINER" \
    >/dev/null 2>&1 || true
  docker volume rm "$DB_VOLUME" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup # in case a previous run died mid-way and left same-named resources

rm -rf "$WORK"
mkdir -p "$WORK"

# ── Network + database ───────────────────────────────────────────────────────
echo "==> creating $NET"
docker network create "$NET" >/dev/null

echo "==> starting Postgres ($POSTGRES_IMAGE)"
docker volume create "$DB_VOLUME" >/dev/null
docker run -d --name "$DB_CONTAINER" --network "$NET" \
  -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD="$DB_PASSWORD" -e POSTGRES_DB=postgres \
  -v "$DB_VOLUME":/var/lib/postgresql/data \
  "$POSTGRES_IMAGE" >/dev/null

echo "==> waiting for Postgres"
for _ in $(seq 1 60); do
  docker exec "$DB_CONTAINER" pg_isready -U odoo >/dev/null 2>&1 && break
  sleep 1
done
docker exec "$DB_CONTAINER" pg_isready -U odoo >/dev/null 2>&1 \
  || { echo "REFUSING: Postgres never became ready"; exit 1; }

# ── Install the module into a fresh database ─────────────────────────────────
# The official `odoo` image's entrypoint adds /mnt/extra-addons to the addons
# path automatically. We mount a module folder NAMED pulse_analytics directly
# under it, matching this repo's own layout (one module at the repo root).
#
#   addons_src  the directory bind-mounted as /mnt/extra-addons/pulse_analytics
#   db_name     the database this run installs into
#   modules     comma-separated -i list (default: website,pulse_analytics).
#               The negative-control call below passes "website" alone so
#               pulse_analytics is mounted but genuinely never installed —
#               passing the wrong default here silently defeated that control
#               on the first real run (it installed pulse_analytics into
#               pulse_verify_control too, so the "negative" control was
#               serving the tag same as the real case).
install_and_init() {
  local addons_src="$1" db_name="$2" container_suffix="$3" modules="${4:-website,pulse_analytics}"
  echo "==> installing into database '$db_name' from $addons_src (modules: $modules)"
  docker run --rm --name "${APP_CONTAINER}-${container_suffix}" --network "$NET" \
    -e HOST="$DB_CONTAINER" -e USER=odoo -e PASSWORD="$DB_PASSWORD" \
    -v "$addons_src":/mnt/extra-addons/pulse_analytics:ro \
    "$ODOO_IMAGE" \
    odoo -d "$db_name" -i "$modules" --without-demo=all --stop-after-init
}

# Positive case: the real module, unmodified.
install_and_init "$MODULE_SRC" pulse_verify init
INSTALL_STATUS=$?

if [ "$MUTATE" -eq 0 ] && [ "$INSTALL_STATUS" -ne 0 ]; then
  echo "REFUSING: the unmodified module failed to install — fix the module before checking its output"
  exit 1
fi

# Negative control database: website only, this module never installed. Same
# image, same addons mount (harmless — it is just never passed to -i), proves
# the checks below are not seeing a tag that was already baked into the base
# image or into some other addon.
install_and_init "$MODULE_SRC" pulse_verify_control control-init website >/dev/null
CONTROL_INSTALL_STATUS=$?
[ "$CONTROL_INSTALL_STATUS" -eq 0 ] \
  || { echo "REFUSING: the control database (no pulse_analytics) failed to even install website"; exit 1; }

# ── --mutate: prove the checks can fail, on a THIRD, disposable database ────
MUTATED_DB=""
if [ "$MUTATE" -eq 1 ]; then
  echo "==> --mutate: breaking a copy of the module, never the real files"
  MUTANT_SRC="$WORK/mutant/pulse_analytics"
  mkdir -p "$(dirname "$MUTANT_SRC")"
  cp -R "$MODULE_SRC" "$MUTANT_SRC"
  # Point the inherit at a view that does not exist. This is expected to make
  # the module FAIL TO INSTALL (Odoo raises on an unknown inherit_id), which
  # is itself the red result this mode exists to demonstrate — a module that
  # cannot even install cannot possibly ship its tag.
  sed -i.bak 's/website\.layout/website.layout_DOES_NOT_EXIST/' \
    "$MUTANT_SRC/views/pulse_tracker.xml"
  rm -f "$MUTANT_SRC/views/pulse_tracker.xml.bak"
  MUTATED_DB="pulse_verify_mutant"
  install_and_init "$MUTANT_SRC" "$MUTATED_DB" mutant-init
  MUTANT_INSTALL_STATUS=$?
  if [ "$MUTANT_INSTALL_STATUS" -eq 0 ]; then
    echo "    ❌ --mutate: the broken module installed anyway — the mutation did not break what it was meant to"
    FAILURES=$((FAILURES + 1))
  else
    echo "    ✅ --mutate: the broken module correctly failed to install (exit $MUTANT_INSTALL_STATUS)"
  fi
fi

# ── Serve the positive-case database and read its HTML ───────────────────────
echo "==> starting Odoo to serve 'pulse_verify'"
# --http-interface=0.0.0.0: Odoo 20.0 changed tools/config.py's default for
# --http-interface to 127.0.0.1 (previously effectively "all interfaces" —
# config['http_interface'] or '0.0.0.0' is the fallback, but 20.0 adds "ensure
# default http_interface is set" and hardcodes 127.0.0.1 when unset). The
# server then binds and logs "HTTP service running on 127.0.0.1:8069" — loopback
# INSIDE the container's own network namespace, which Docker's -p publish
# cannot reach (it forwards to the container's external interface, not its
# loopback). Confirmed with docker exec curl: 127.0.0.1:8069 inside the
# container answers 200, the container's own bridge IP answers nothing. First
# real run of this script hung on "waiting for http://127.0.0.1:18069/" and
# then failed with "did not return a real page (got 0 bytes)" for exactly
# this reason — not a problem with the module.
docker run -d --name "$APP_CONTAINER" --network "$NET" -p "${HTTP_PORT}:8069" \
  -e HOST="$DB_CONTAINER" -e USER=odoo -e PASSWORD="$DB_PASSWORD" \
  -v "$MODULE_SRC":/mnt/extra-addons/pulse_analytics:ro \
  "$ODOO_IMAGE" \
  odoo -d pulse_verify "--db-filter=^pulse_verify\$" --http-interface=0.0.0.0 >/dev/null

echo "==> waiting for http://127.0.0.1:${HTTP_PORT}/"
for _ in $(seq 1 60); do
  curl -sf -o /dev/null "http://127.0.0.1:${HTTP_PORT}/" && break
  sleep 1
done

HOME_HTML=$(curl -s "http://127.0.0.1:${HTTP_PORT}/")
# Odoo's backend/login surface — never the site this module targets.
LOGIN_HTML=$(curl -s "http://127.0.0.1:${HTTP_PORT}/web/login")

# A "not present" result from an empty/failed fetch is not evidence — it is a
# timeout wearing the same face as a real negative. Every absence check below
# must first prove the page it is reading actually loaded, or a stalled Odoo
# boot would make every "no ciphera reference" check pass vacuously.
require_real_page() {
  local label="$1" html="$2"
  if ! printf '%s' "$html" | grep -qi '<html'; then
    echo "REFUSING: $label did not return a real page (got ${#html} bytes) — the server may not be up"
    exit 1
  fi
}
require_real_page "the homepage" "$HOME_HTML"
require_real_page "the backend login page" "$LOGIN_HTML"

echo
echo "==> checking the served HTML"

TAGS=$(printf '%s' "$HOME_HTML" | grep -oE '<script[^>]*ciphera[^>]*></script>' | tr '\n' ' ')

check_pass() { echo "    ✅ $1"; }
check_fail() { echo "    ❌ $1"; FAILURES=$((FAILURES + 1)); }

if printf '%s' "$TAGS" | grep -qE "$TAG_PATTERN"; then
  check_pass "the homepage carries the exact Pulse tracker src"
else
  check_fail "the homepage does not carry the exact Pulse tracker src (got: ${TAGS:-<nothing>})"
fi

if printf '%s' "$TAGS" | grep -qE 'defer(="defer")?'; then
  check_pass "the tag carries defer"
else
  check_fail "the tag has no defer attribute (got: ${TAGS:-<nothing>})"
fi

if printf '%s' "$TAGS" | grep -q 'data-domain'; then
  check_fail "the tag unexpectedly carries data-domain — this module ships auto-detect only (got: $TAGS)"
else
  check_pass "no data-domain — auto-detect, as designed"
fi

SCRIPT_COUNT=$(printf '%s' "$HOME_HTML" | grep -oE '<script[^>]*ciphera[^>]*>' | wc -l | tr -d ' ')
if [ "$SCRIPT_COUNT" = "1" ]; then
  check_pass "exactly one ciphera script tag (no companion script — this module does not offer one)"
else
  check_fail "expected exactly one ciphera script tag, found $SCRIPT_COUNT"
fi

# Negative control, same page: the backend must carry nothing.
if printf '%s' "$LOGIN_HTML" | grep -qi 'ciphera'; then
  check_fail "the backend login page carries a reference to ciphera — this module must never reach /web"
else
  check_pass "the backend carries no reference to ciphera"
fi

# ── Second positive instance, against the control database: no module, no tag ─
# Reuse the same running Odoo process against a different, --db-filter'd
# request is not possible without restarting it, so spin a short-lived second
# instance bound to a different host port against the control database.
CONTROL_PORT=$((HTTP_PORT + 1))
echo "==> starting a second Odoo instance to serve the no-module control database on :${CONTROL_PORT}"
docker run -d --name "${APP_CONTAINER}-control" --network "$NET" -p "${CONTROL_PORT}:8069" \
  -e HOST="$DB_CONTAINER" -e USER=odoo -e PASSWORD="$DB_PASSWORD" \
  "$ODOO_IMAGE" \
  odoo -d pulse_verify_control "--db-filter=^pulse_verify_control\$" --http-interface=0.0.0.0 >/dev/null

for _ in $(seq 1 60); do
  curl -sf -o /dev/null "http://127.0.0.1:${CONTROL_PORT}/" && break
  sleep 1
done
CONTROL_HTML=$(curl -s "http://127.0.0.1:${CONTROL_PORT}/")
require_real_page "the no-module control homepage" "$CONTROL_HTML"

if printf '%s' "$CONTROL_HTML" | grep -qi 'ciphera'; then
  check_fail "negative control: a site WITHOUT this module already shows a ciphera reference — the harness is not measuring what it claims to"
else
  check_pass "negative control: a site without this module installed carries no ciphera reference"
fi

echo
if [ "$FAILURES" -eq 0 ]; then
  echo "Odoo ($ODOO_IMAGE): ALL CHECKS PASSED"
else
  echo "Odoo ($ODOO_IMAGE): $FAILURES FAILURE(S)"
fi
exit "$FAILURES"
