# Contributing

Keep changes small, authorized, and reproducible.

Do not add targets, credentials, reports, logs, or private evidence to Git.
Pin an upstream revision when adding a new runtime dependency or skill.

Run this check before a pull request:

```sh
./scripts/check.sh
```

The check validates shell syntax, JSON configuration, OpenCode configuration,
and the optional lab Compose file. It does not build the lab image or run a
security assessment.

For a runtime change, test the changed backend separately and record the
backend, operating system, and result in the pull request. Do not claim tool
coverage from a configuration check.
