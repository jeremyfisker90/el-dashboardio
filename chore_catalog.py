#!/usr/bin/env python3
"""A starter family chore catalog.

Instructions are lifted from the family's own "Cleaning Jobs.xlsx" so they name the
actual supplies and spots (blue bucket, Murphy's oil soap, blue Pledge, push broom,
command center) rather than generic advice.

Points scale: the weekly target is 100/kid, so quick jobs sit at 5-10, everyday
jobs 10-20, and the heavy or unpleasant ones 25-40.

Frequency drives the rotation: weekly / bi-weekly / monthly.
"""

# name, points, kind, frequency, description
CATALOG = [
    # ---------------- kitchen, everyday ----------------
    ("Load the dishwasher", 10, "required", "weekly",
     "Clear the counters and table first. Scrape plates into the trash, then load "
     "everything in — plates on the bottom, cups and bowls on top. Start it if it's full."),

    ("Put away the clean dishes", 10, "required", "weekly",
     "Empty the dishwasher and put everything where it belongs. Anything still wet "
     "goes on the drying towel, not back in the cupboard."),

    ("Wash the pans by hand", 10, "required", "weekly",
     "The pots, pans and knives that don't go in the dishwasher. Wash them, then set "
     "them on the drying towel on the counter."),

    ("Wipe down the kitchen counters", 10, "required", "weekly",
     "Clear the clutter and put it away first, then wipe every counter with the "
     "counter cleaner. Get the crumbs at the back edge too."),

    ("Clear and wipe the kitchen table", 10, "required", "weekly",
     "Everything on the table gets put away — if you don't know where it goes, put it "
     "in the bin. Then wipe the whole table down with the table cleaner."),

    ("Make dinner", 30, "required", "weekly",
     "Check the Dinners list on the tablet for what's planned. Get everything out, "
     "cook it, and put the ingredients away as you go. Clean up your prep mess."),

    # ---------------- everyday life ----------------
    ("Do a load of laundry", 15, "required", "weekly",
     "Sort it, wash it, dry it, then FOLD it and put it away. A basket of clean "
     "laundry sitting in the hall doesn't count as done."),

    ("Walk the dog", 10, "required", "weekly",
     "A real walk around the block, not just out to the yard. Take a bag and clean up "
     "after him. Fresh water in the bowl when you get back."),

    ("Clean your bedroom", 20, "required", "weekly",
     "Make the bed. Clothes off the floor — dirty ones in the hamper, clean ones "
     "folded and put away. Clutter off the floor. Wipe the desk and shelves with the "
     "blue Pledge and a rag. Vacuum the floor last."),

    # ---------------- family room ----------------
    ("Tidy the family room", 15, "required", "weekly",
     "Clear all the tables of clutter and put it away — if you don't know where "
     "something goes, put it in the bin. Wipe the tables and the command center desk "
     "(brush the dust onto the floor, it gets vacuumed later). Fold the blankets into "
     "the blanket basket and straighten the pillows."),

    # ---------------- floors ----------------
    ("Sweep the 1st floor", 15, "required", "weekly",
     "Check the push broom is clean first — use the hand vacuum and brush the trash "
     "off it. Then sweep the family room, entry way, dining room and kitchen. Pull the "
     "chairs out from the command center and kitchen table and get underneath."),

    ("Vacuum the 1st floor", 20, "required", "weekly",
     "Whole floor — family room, dining room, entry. Move the chairs out and get under "
     "the tables. Do the edges along the walls, not just the middle."),

    ("Mop the 1st floor", 20, "required", "bi-weekly",
     "Sweep or vacuum first, otherwise you're just pushing dirt around. Then mop all "
     "the hard floors and let them dry before anyone walks on them."),

    ("Vacuum the basement", 15, "required", "bi-weekly",
     "The whole basement floor including under the couch and around the edges. Pick "
     "the clutter up off the floor before you start."),

    ("Clean the stairs", 20, "required", "bi-weekly",
     "Blue bucket with warm water and Murphy's oil soap. Wipe each stair down with a "
     "rag, working from the top down so you're not stepping on what you just cleaned."),

    # ---------------- deeper cleaning ----------------
    ("Wipe the 1st floor baseboards", 20, "required", "monthly",
     "Blue bucket with warm soapy water (just dish soap) and a rag. Go around every "
     "room on the 1st floor and wipe the baseboards down. They get grimy — you'll see "
     "the rag turn grey."),

    ("Wipe the stairway baseboards", 15, "required", "monthly",
     "Blue bucket, warm water, Murphy's oil soap. Wipe the baseboards running up "
     "alongside the stairs."),

    ("Clean the shared bathroom", 30, "required", "bi-weekly",
     "Clutter off the counter. Wipe the counter and sink with a Clorox wipe. Mop the "
     "floor in the sink room and wipe the shower room floor with a Clorox wipe. Wipe "
     "the toilet and the baseboards and wall around it BEFORE you clean the bowl. Then "
     "toilet bowl cleaner under the rim, scrub with the brush, and rest the brush on "
     "the rim with the lid set on top so it drips dry — don't flush it."
     "  ⚠ Clorox wipes bleach clothes. Don't let them touch anything you care about."),

    ("Dust the family room and command center", 10, "optional", "monthly",
     "Blue Pledge and a rag on the tables, shelves and the command center desk. Work "
     "top down so the dust falls to the floor, then vacuum."),

    # ---------------- optional, extra points ----------------
    ("Wash the car", 25, "optional", "monthly",
     "Hose it down, soap bucket, dry with the towels in the garage."),

    ("Clean out the car", 15, "optional", "monthly",
     "Trash out, everything that belongs in the house back in the house, then vacuum "
     "the seats and floor mats."),

    ("Take out trash & recycling", 15, "required", "weekly",
     "Empty every bin in the house, replace the bags, and take the cans to the curb."),

    ("Sweep the garage", 15, "optional", "monthly",
     "Push broom the whole garage floor and get the cobwebs out of the corners."),

    ("Wipe down the kitchen appliance fronts", 10, "optional", "monthly",
     "Fridge, dishwasher, oven and microwave fronts — fingerprints and splatters. "
     "Stainless gets wiped with the grain, not in circles."),
]


if __name__ == "__main__":
    import json
    print(json.dumps([
        {"name": n, "points": p, "kind": k, "frequency": f, "description": d}
        for (n, p, k, f, d) in CATALOG
    ], indent=1))
    req = [c for c in CATALOG if c[2] == "required"]
    print("\n%d chores (%d required, %d optional)" % (len(CATALOG), len(req), len(CATALOG) - len(req)))
    for freq in ("weekly", "bi-weekly", "monthly"):
        rows = [c for c in CATALOG if c[3] == freq]
        print("  %-10s %2d chores, %3d pts" % (freq, len(rows), sum(c[1] for c in rows)))
