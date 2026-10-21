# Security policy

## Reporting a vulnerability

Please do not open a public issue for a security problem.

Report it privately through GitHub: open the [Security tab](https://github.com/Cl0ud-9/Weather-Prediction-Model/security)
and choose **Report a vulnerability**, or go straight to
[the advisory form](https://github.com/Cl0ud-9/Weather-Prediction-Model/security/advisories/new). Only the maintainer
sees what you send.

Please include what you found, how to reproduce it, and what you think an attacker could do with it. The maintainer
aims to answer within a week, and you will be credited in the fix unless you would rather not be.

## What counts

- A way for a data file or a command-line argument to make `predict.py` run code or read files outside the data
  folder it was pointed at.

Not in scope: problems in pandas or scikit-learn themselves (report those upstream).

## Supported versions

Only the current `main` gets fixes.
