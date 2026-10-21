# Notebooks

`original_notebook.ipynb` is the first version of the project, from the third-year AI course in 2024, kept as it was.
It was written following a Dataquest walkthrough on weather prediction.

It reads the city files from the folder it runs in, so to run it, copy the files from [../data](../data) next to it.

It is kept for the record, not as the current method. It treats each hourly row as a day: its target is the next
row, one hour later, and the maximum and minimum temperature and UV index it predicts are daily values that repeat on
every hourly row, so the "next" value is usually already in the input. That makes its accuracy look much higher than
it is. The [weather](../weather) package fixes this by working with whole days; the README's results come from it.
