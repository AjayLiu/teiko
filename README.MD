I first looked at the data `cell-count.csv` and thought about what tables would make sense to be modeled in this scenario.

I see that every row has a project ID, subject ID, info about the subject, and a sample alongside the sample results.

Quickly scanning through the data I saw that each project can have many subjects, each of which can have many samples.

Hence, a table for projects, subjects, and samples with one-to-many relationships from left to right seems to be most fitting.
