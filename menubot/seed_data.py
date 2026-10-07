"""Starter recipes, loaded into an empty database.

Compact format so they're easy to edit. Each ingredient line is
    qty | unit | item | aisle | note
with qty blank for "to taste" and a trailing * on the aisle for pantry staples.
"""

from .models import Ingredient, RecipeIn


def _ings(block: str) -> list[Ingredient]:
    out = []
    for line in block.strip().splitlines():
        qty, unit, item, aisle, *note = [p.strip() for p in line.split("|")]
        staple = aisle.endswith("*")
        out.append(Ingredient(
            item=item, qty=float(qty) if qty else None, unit=unit,
            aisle=aisle.rstrip("*"), staple=staple, note=note[0] if note else "",
        ))
    return out


def R(title, description, servings, minutes, cuisine, protein, tags, ingredients, steps) -> RecipeIn:
    return RecipeIn(
        title=title, description=description, servings=servings, total_minutes=minutes,
        cuisine=cuisine, protein=protein, tags=[t.strip() for t in tags.split(",")],
        ingredients=_ings(ingredients), steps=steps,
    )


SEED = [
    # ---------------- vegetarian / vegan ----------------
    R("Crispy Chickpea Shawarma Bowls", "Sheet-pan spiced chickpeas and cauliflower over rice with a lemony tahini sauce.",
      4, 40, "Middle Eastern", "vegan", "sheet-pan, bowl, weeknight", """
      2 | can | chickpeas | pantry | drained and patted dry
      1 | head | cauliflower | produce | cut into florets
      1 | | red onion | produce | cut into wedges
      3 | tbsp | olive oil | pantry*
      2 | tsp | ground cumin | spices*
      1 | tsp | smoked paprika | spices*
      0.5 | tsp | ground cinnamon | spices*
      1.5 | cup | basmati rice | pantry
      0.33 | cup | tahini | pantry
      1 | | lemon | produce
      1 | clove | garlic | produce | grated
      1 | | english cucumber | produce | diced
      1 | cup | cherry tomatoes | produce | halved
      0.5 | cup | parsley | produce | chopped
      | | salt | spices*
      """, [
          "Heat oven to 425°F. Toss chickpeas, cauliflower and onion with oil, cumin, paprika, cinnamon and 1 tsp salt on a sheet pan.",
          "Roast 25 to 30 minutes, tossing once, until the chickpeas are crisp and the cauliflower is charred.",
          "Meanwhile cook the rice according to package directions.",
          "Whisk tahini, juice of the lemon, garlic, a pinch of salt and 4 to 6 tbsp water until pourable.",
          "Build bowls with rice, roasted vegetables, cucumber, tomatoes and parsley; drizzle with tahini sauce.",
      ]),
    R("Black Bean Sweet Potato Tacos", "Roasted sweet potatoes and smoky black beans with a quick lime crema.",
      4, 35, "Mexican", "vegetarian", "tacos, weeknight, sheet-pan", """
      2 | | sweet potato | produce | 1/2-inch cubes
      2 | tbsp | olive oil | pantry*
      1 | tsp | chili powder | spices*
      1 | tsp | ground cumin | spices*
      1 | can | black beans | pantry | drained
      8 | | corn tortilla | bakery
      0.5 | cup | sour cream | dairy
      2 | | lime | produce
      0.5 | cup | cilantro | produce
      0.5 | cup | cotija cheese | dairy | crumbled
      0.25 | | red cabbage | produce | thinly sliced
      | | salt | spices*
      """, [
          "Heat oven to 425°F. Toss sweet potatoes with oil, chili powder, cumin and salt; roast 25 minutes.",
          "Warm black beans in a small pot with a splash of water and a pinch of salt; lightly mash.",
          "Stir sour cream with the juice of 1 lime and a pinch of salt.",
          "Char tortillas over a gas flame or in a dry skillet.",
          "Fill tortillas with beans, sweet potatoes, cabbage, cotija, cilantro and lime crema. Serve with lime wedges.",
      ]),
    R("Creamy Tomato Tortellini Soup", "A 25-minute soup with cheese tortellini, spinach and a splash of cream.",
      4, 25, "Italian", "vegetarian", "soup, one-pot, quick", """
      2 | tbsp | olive oil | pantry*
      1 | | yellow onion | produce | diced
      3 | clove | garlic | produce | minced
      1 | can | crushed tomatoes | pantry | 28 oz
      4 | cup | vegetable broth | pantry
      20 | oz | cheese tortellini | dairy | refrigerated
      0.5 | cup | heavy cream | dairy
      5 | oz | baby spinach | produce
      0.5 | cup | parmesan | dairy | grated
      1 | tsp | dried oregano | spices*
      | | salt | spices*
      | | black pepper | spices*
      """, [
          "Heat oil in a large pot over medium. Cook onion until soft, 5 minutes; add garlic and oregano for 1 minute.",
          "Add tomatoes and broth; simmer 10 minutes.",
          "Add tortellini and cook until tender, about 3 minutes.",
          "Stir in cream and spinach until wilted. Season with salt and pepper; serve topped with parmesan.",
      ]),
    R("Mushroom Stroganoff", "Deeply browned mushrooms in a tangy sour cream sauce over egg noodles.",
      4, 30, "Eastern European", "vegetarian", "pasta, comfort, weeknight", """
      1.5 | lb | cremini mushrooms | produce | sliced
      3 | tbsp | butter | dairy*
      1 | | yellow onion | produce | thinly sliced
      2 | clove | garlic | produce | minced
      1 | tbsp | all-purpose flour | pantry*
      1.5 | cup | vegetable broth | pantry
      1 | tbsp | dijon mustard | pantry
      0.75 | cup | sour cream | dairy
      12 | oz | egg noodles | pantry
      0.25 | cup | dill | produce | chopped
      | | salt | spices*
      | | black pepper | spices*
      """, [
          "Cook noodles in salted water; drain.",
          "Brown mushrooms in 2 tbsp butter over high heat in batches, without crowding, 8 minutes. Season and set aside.",
          "Melt remaining butter, cook onion 5 minutes, add garlic and flour and stir 1 minute.",
          "Whisk in broth and mustard, simmer until thickened, then return mushrooms.",
          "Off heat, stir in sour cream. Serve over noodles with dill.",
      ]),
    R("Chana Masala", "Weeknight chickpea curry with tomatoes, ginger and garam masala.",
      4, 35, "Indian", "vegan", "curry, one-pot, make-ahead", """
      2 | tbsp | neutral oil | pantry*
      1 | | yellow onion | produce | finely chopped
      4 | clove | garlic | produce | minced
      1 | tbsp | ginger | produce | grated
      1 | | serrano chile | produce | minced
      2 | tsp | garam masala | spices*
      1 | tsp | ground cumin | spices*
      1 | tsp | ground turmeric | spices*
      1 | can | diced tomatoes | pantry
      2 | can | chickpeas | pantry | drained
      1.5 | cup | basmati rice | pantry
      1 | | lemon | produce
      0.5 | cup | cilantro | produce
      | | salt | spices*
      """, [
          "Cook rice according to package directions.",
          "Heat oil over medium-high; cook onion until golden, 8 minutes.",
          "Add garlic, ginger, chile and spices; stir 1 minute.",
          "Add tomatoes, chickpeas and 1 cup water; simmer 15 minutes, mashing some chickpeas to thicken.",
          "Season with salt and lemon juice; top with cilantro and serve with rice.",
      ]),
    R("Pesto Gnocchi with Burst Tomatoes", "Pan-crisped gnocchi tossed with cherry tomatoes, pesto and mozzarella.",
      4, 20, "Italian", "vegetarian", "quick, one-pan, weeknight", """
      2 | lb | shelf-stable gnocchi | pantry
      3 | tbsp | olive oil | pantry*
      2 | pint | cherry tomatoes | produce
      2 | clove | garlic | produce | sliced
      0.5 | cup | basil pesto | pantry
      8 | oz | fresh mozzarella | dairy | torn
      0.5 | cup | basil | produce
      | | salt | spices*
      """, [
          "Heat 2 tbsp oil in a large skillet over medium-high. Add gnocchi in one layer and cook until golden on both sides, 8 minutes. Remove.",
          "Add remaining oil, tomatoes and garlic; cook until tomatoes burst, 5 minutes.",
          "Return gnocchi, stir in pesto and a splash of water. Season with salt.",
          "Top with mozzarella and basil.",
      ]),
    R("Spinach and Feta Spanakopita Pie", "All the flavor of spanakopita in an easy skillet pie with phyllo on top.",
      4, 50, "Greek", "vegetarian", "baked, make-ahead", """
      20 | oz | frozen chopped spinach | frozen | thawed and squeezed dry
      8 | oz | feta | dairy | crumbled
      0.5 | cup | ricotta | dairy
      3 | | egg | dairy
      4 | | scallion | produce | sliced
      0.5 | cup | dill | produce | chopped
      1 | | lemon | produce | zested
      8 | | phyllo sheet | frozen | thawed
      4 | tbsp | butter | dairy* | melted
      | | black pepper | spices*
      """, [
          "Heat oven to 375°F.",
          "Mix spinach, feta, ricotta, eggs, scallions, dill, lemon zest and pepper.",
          "Brush a 10-inch skillet with butter, spread in the filling.",
          "Layer phyllo on top, brushing each sheet with butter and scrunching the edges.",
          "Bake until deep golden, 30 to 35 minutes. Rest 5 minutes before slicing.",
      ]),
    R("Vegetable Fried Rice", "Better-than-takeout fried rice with eggs, peas and carrots.",
      4, 20, "Chinese", "vegetarian", "quick, weeknight, leftovers", """
      4 | cup | cooked rice | pantry | day-old
      3 | tbsp | neutral oil | pantry*
      4 | | egg | dairy | beaten
      1 | cup | frozen peas and carrots | frozen
      4 | | scallion | produce | sliced
      3 | clove | garlic | produce | minced
      1 | tbsp | ginger | produce | grated
      3 | tbsp | soy sauce | pantry*
      1 | tsp | toasted sesame oil | pantry
      """, [
          "Heat 1 tbsp oil in a wok over high; scramble eggs until just set, then remove.",
          "Add remaining oil, scallion whites, garlic and ginger; stir 30 seconds.",
          "Add rice and press into the pan; let crisp 2 minutes before tossing. Repeat twice.",
          "Add peas and carrots, soy sauce and sesame oil; toss until hot.",
          "Fold in eggs and scallion greens.",
      ]),
    R("Peanut Noodles with Crispy Tofu", "Chewy noodles in a spicy peanut-lime sauce with golden tofu and crunchy vegetables.",
      4, 30, "Asian", "vegan", "noodles, weeknight", """
      14 | oz | extra-firm tofu | produce | pressed and cubed
      2 | tbsp | cornstarch | pantry
      3 | tbsp | neutral oil | pantry*
      12 | oz | lo mein noodles | pantry
      0.5 | cup | creamy peanut butter | pantry
      3 | tbsp | soy sauce | pantry*
      2 | tbsp | rice vinegar | pantry*
      1 | tbsp | maple syrup | pantry
      1 | tbsp | chili crisp | pantry
      2 | | lime | produce
      1 | | red bell pepper | produce | thinly sliced
      1 | | english cucumber | produce | cut into matchsticks
      0.25 | cup | roasted peanuts | pantry | chopped
      """, [
          "Toss tofu with cornstarch and a pinch of salt. Fry in oil over medium-high until crisp on all sides, 10 minutes.",
          "Cook noodles according to package; rinse under cold water.",
          "Whisk peanut butter, soy sauce, vinegar, maple, chili crisp, juice of 1 lime and hot water until smooth.",
          "Toss noodles with sauce, bell pepper and cucumber. Top with tofu, peanuts and lime wedges.",
      ]),
    R("Shakshuka", "Eggs poached in a spiced pepper and tomato sauce, served with crusty bread.",
      4, 30, "North African", "vegetarian", "eggs, one-pan, brunch-for-dinner", """
      2 | tbsp | olive oil | pantry*
      1 | | yellow onion | produce | sliced
      2 | | red bell pepper | produce | sliced
      3 | clove | garlic | produce | sliced
      2 | tsp | ground cumin | spices*
      1 | tsp | smoked paprika | spices*
      1 | can | crushed tomatoes | pantry | 28 oz
      6 | | egg | dairy
      4 | oz | feta | dairy
      0.25 | cup | cilantro | produce
      1 | | crusty bread loaf | bakery
      | | salt | spices*
      """, [
          "Heat oil in a large skillet; cook onion and peppers until soft, 10 minutes.",
          "Add garlic and spices for 1 minute, then tomatoes. Simmer 10 minutes and season.",
          "Make 6 wells and crack in the eggs. Cover and cook until whites are set, 6 to 8 minutes.",
          "Top with feta and cilantro; serve with bread.",
      ]),
    R("Butternut Squash Risotto", "Creamy, cozy risotto with roasted squash and sage brown butter.",
      4, 50, "Italian", "vegetarian", "cozy, fall", """
      1 | | butternut squash | produce | peeled, 1/2-inch cubes
      2 | tbsp | olive oil | pantry*
      6 | cup | vegetable broth | pantry
      1 | | shallot | produce | minced
      1.5 | cup | arborio rice | pantry
      0.5 | cup | dry white wine | pantry
      0.75 | cup | parmesan | dairy | grated
      3 | tbsp | butter | dairy*
      10 | | sage leaf | produce
      | | salt | spices*
      """, [
          "Roast squash with 1 tbsp oil and salt at 425°F until tender, 25 minutes.",
          "Warm broth in a pot. In another pot cook shallot in remaining oil, then toast rice 2 minutes.",
          "Add wine, then broth a ladle at a time, stirring often, until rice is creamy and al dente, about 20 minutes.",
          "Stir in half the squash (mashed) and parmesan; fold in the rest.",
          "Brown butter with sage leaves until nutty and spoon over each bowl.",
      ]),
    R("Lentil Bolognese", "Hearty lentil and mushroom ragù that tastes like it simmered all day.",
      4, 45, "Italian", "vegan", "pasta, make-ahead, freezer-friendly", """
      3 | tbsp | olive oil | pantry*
      1 | | yellow onion | produce | finely chopped
      1 | | carrot | produce | finely chopped
      1 | | celery stalk | produce | finely chopped
      8 | oz | cremini mushrooms | produce | finely chopped
      3 | clove | garlic | produce | minced
      2 | tbsp | tomato paste | pantry
      1 | cup | brown lentils | pantry | rinsed
      1 | can | crushed tomatoes | pantry | 28 oz
      3 | cup | vegetable broth | pantry
      1 | lb | rigatoni | pantry
      | | salt | spices*
      | | black pepper | spices*
      """, [
          "Cook onion, carrot, celery and mushrooms in oil over medium-high until browned, 12 minutes.",
          "Add garlic and tomato paste; cook 2 minutes.",
          "Add lentils, tomatoes and broth; simmer partially covered until lentils are tender, 25 minutes.",
          "Cook rigatoni; toss with sauce and a splash of pasta water. Season well.",
      ]),
    R("Halloumi Grain Bowls", "Seared halloumi over farro with roasted broccoli, olives and lemon vinaigrette.",
      4, 35, "Mediterranean", "vegetarian", "bowl, meal-prep", """
      1.5 | cup | farro | pantry
      1 | head | broccoli | produce | florets
      3 | tbsp | olive oil | pantry*
      8 | oz | halloumi | dairy | sliced
      0.5 | cup | kalamata olives | pantry | halved
      1 | cup | cherry tomatoes | produce | halved
      1 | | lemon | produce
      1 | tsp | dijon mustard | pantry
      1 | tsp | honey | pantry
      | | salt | spices*
      """, [
          "Simmer farro in salted water until tender, 25 to 30 minutes; drain.",
          "Roast broccoli with 1 tbsp oil and salt at 425°F for 20 minutes.",
          "Whisk lemon juice, mustard, honey and 2 tbsp oil.",
          "Sear halloumi in a dry nonstick skillet until golden, 2 minutes per side.",
          "Toss farro with dressing; top with broccoli, tomatoes, olives and halloumi.",
      ]),
    R("Thai Red Curry with Vegetables", "Coconut red curry loaded with vegetables and tofu.",
      4, 30, "Thai", "vegan", "curry, weeknight", """
      1 | tbsp | neutral oil | pantry*
      3 | tbsp | red curry paste | pantry
      2 | can | coconut milk | pantry
      14 | oz | extra-firm tofu | produce | cubed
      1 | | red bell pepper | produce | sliced
      1 | | zucchini | produce | half-moons
      2 | cup | snap peas | produce
      1 | tbsp | soy sauce | pantry*
      1 | tsp | brown sugar | pantry*
      1 | | lime | produce
      0.5 | cup | thai basil | produce
      1.5 | cup | jasmine rice | pantry
      """, [
          "Cook rice according to package directions.",
          "Fry curry paste in oil 1 minute; whisk in coconut milk and bring to a simmer.",
          "Add tofu and bell pepper; simmer 5 minutes. Add zucchini and snap peas; simmer 4 minutes more.",
          "Season with soy sauce, sugar and lime juice; stir in basil. Serve over rice.",
      ]),
    R("Caprese Grilled Cheese with Tomato Soup", "Mozzarella, pesto and tomato grilled cheese with a quick blender tomato soup.",
      2, 25, "American", "vegetarian", "comfort, quick, sandwich", """
      4 | slice | sourdough bread | bakery
      6 | oz | fresh mozzarella | dairy | sliced
      2 | tbsp | basil pesto | pantry
      1 | | tomato | produce | sliced
      2 | tbsp | butter | dairy*
      1 | can | whole peeled tomatoes | pantry | 28 oz
      1 | cup | vegetable broth | pantry
      0.25 | cup | heavy cream | dairy
      1 | clove | garlic | produce
      | | salt | spices*
      """, [
          "Simmer tomatoes, broth and garlic 10 minutes; blend with cream and season.",
          "Spread pesto on bread, layer mozzarella and tomato, close sandwiches.",
          "Butter the outsides and cook over medium-low until golden and melty, 4 minutes per side.",
          "Serve with soup for dunking.",
      ]),
    R("Eggplant Parmesan Bake", "Roasted (not fried) eggplant layered with marinara and mozzarella.",
      4, 60, "Italian", "vegetarian", "baked, comfort", """
      2 | | eggplant | produce | 1/2-inch rounds
      3 | tbsp | olive oil | pantry*
      3 | cup | marinara sauce | pantry
      12 | oz | low-moisture mozzarella | dairy | shredded
      0.75 | cup | parmesan | dairy | grated
      0.5 | cup | panko breadcrumbs | pantry
      0.5 | cup | basil | produce
      | | salt | spices*
      """, [
          "Heat oven to 425°F. Brush eggplant with oil, salt, and roast on sheet pans 20 minutes, flipping once.",
          "Layer marinara, eggplant, mozzarella and parmesan in a baking dish, repeating 2 to 3 times.",
          "Top with panko tossed with a little oil.",
          "Bake at 400°F until bubbling and browned, 25 minutes. Top with basil.",
      ]),
    R("Pasta e Ceci", "Roman-style chickpea and pasta stew with rosemary and parmesan.",
      4, 30, "Italian", "vegetarian", "one-pot, cozy, pantry", """
      3 | tbsp | olive oil | pantry*
      4 | clove | garlic | produce | sliced
      1 | sprig | rosemary | produce
      2 | tbsp | tomato paste | pantry
      2 | can | chickpeas | pantry | drained
      5 | cup | vegetable broth | pantry
      1 | cup | ditalini | pantry
      0.5 | cup | parmesan | dairy | grated
      0.25 | tsp | red pepper flakes | spices*
      | | salt | spices*
      """, [
          "Warm oil with garlic, rosemary and pepper flakes until fragrant. Stir in tomato paste for 1 minute.",
          "Add chickpeas and broth; simmer 10 minutes, then mash about a third of the chickpeas.",
          "Add pasta and cook until tender, stirring often, adding water if it gets too thick.",
          "Remove rosemary; stir in parmesan, season and finish with olive oil.",
      ]),
    R("Veggie Quesadillas with Corn Salsa", "Cheesy black bean, pepper and spinach quesadillas with a fresh corn salsa.",
      4, 25, "Mexican", "vegetarian", "quick, kid-friendly", """
      8 | | flour tortilla | bakery
      12 | oz | monterey jack | dairy | shredded
      1 | can | black beans | pantry | drained
      1 | | red bell pepper | produce | diced
      3 | oz | baby spinach | produce
      1.5 | cup | frozen corn | frozen | thawed
      1 | | jalapeño | produce | minced
      0.25 | | red onion | produce | finely diced
      1 | | lime | produce
      0.25 | cup | cilantro | produce
      1 | tbsp | neutral oil | pantry*
      | | salt | spices*
      """, [
          "Mix corn, jalapeño, red onion, cilantro, lime juice and salt.",
          "Sauté bell pepper in oil 4 minutes; add spinach to wilt.",
          "Fill tortillas with cheese, beans and vegetables; fold.",
          "Cook in a dry skillet until crisp and melted, 3 minutes per side. Serve with corn salsa.",
      ]),
    R("Miso Butter Udon with Mushrooms", "Silky udon in miso butter with seared mushrooms and bok choy.",
      2, 20, "Japanese", "vegetarian", "noodles, quick", """
      2 | package | frozen udon | frozen
      8 | oz | shiitake mushrooms | produce | sliced
      2 | | baby bok choy | produce | halved
      2 | tbsp | white miso | pantry
      3 | tbsp | butter | dairy*
      1 | tbsp | soy sauce | pantry*
      2 | | scallion | produce | sliced
      1 | tbsp | neutral oil | pantry*
      """, [
          "Sear mushrooms in oil over high heat until browned, 5 minutes. Add bok choy for 2 minutes.",
          "Cook udon according to package; reserve 1/2 cup cooking water.",
          "In the skillet, melt butter with miso, soy sauce and a splash of noodle water.",
          "Toss in udon until glossy; top with scallions.",
      ]),

    # ---------------- fish & shellfish ----------------
    R("Miso-Glazed Salmon with Bok Choy", "Broiled salmon with a sweet-salty miso glaze and garlicky greens.",
      4, 25, "Japanese", "fish", "weeknight, quick", """
      1.5 | lb | salmon fillet | seafood | 4 pieces
      3 | tbsp | white miso | pantry
      2 | tbsp | mirin | pantry
      1 | tbsp | soy sauce | pantry*
      1 | tbsp | honey | pantry
      4 | | baby bok choy | produce | halved
      2 | clove | garlic | produce | sliced
      1 | tbsp | neutral oil | pantry*
      1.5 | cup | jasmine rice | pantry
      1 | tsp | sesame seeds | spices*
      """, [
          "Cook rice. Heat broiler with a rack 6 inches from the heat.",
          "Whisk miso, mirin, soy sauce and honey; spread over salmon on a foil-lined pan.",
          "Broil until glaze caramelizes and salmon is just cooked, 7 to 9 minutes.",
          "Stir-fry bok choy and garlic in oil 3 minutes. Serve with salmon and rice; sprinkle sesame seeds.",
      ]),
    R("Teriyaki Salmon Rice Bowls", "Pan-seared salmon in homemade teriyaki with rice, avocado and cucumber.",
      4, 25, "Japanese", "fish", "bowl, weeknight", """
      1.5 | lb | salmon fillet | seafood | 4 pieces
      0.33 | cup | soy sauce | pantry*
      3 | tbsp | mirin | pantry
      2 | tbsp | brown sugar | pantry*
      1 | tbsp | ginger | produce | grated
      1 | clove | garlic | produce | grated
      1 | tsp | cornstarch | pantry
      1.5 | cup | jasmine rice | pantry
      1 | | avocado | produce
      1 | | english cucumber | produce | sliced
      2 | | scallion | produce
      1 | tbsp | neutral oil | pantry*
      """, [
          "Cook rice. Whisk soy, mirin, sugar, ginger, garlic, cornstarch and 1/4 cup water.",
          "Sear salmon skin-side down in oil over medium-high 5 minutes; flip and cook 2 minutes.",
          "Pour in sauce and simmer, spooning over salmon, until glossy, 1 to 2 minutes.",
          "Serve over rice with avocado, cucumber and scallions.",
      ]),
    R("Sheet-Pan Lemon Herb Salmon and Potatoes", "Crispy potatoes and green beans roasted alongside lemony salmon.",
      4, 40, "American", "fish", "sheet-pan, weeknight", """
      1.5 | lb | baby potatoes | produce | halved
      12 | oz | green beans | produce | trimmed
      1.5 | lb | salmon fillet | seafood | 4 pieces
      3 | tbsp | olive oil | pantry*
      1 | | lemon | produce
      2 | clove | garlic | produce | minced
      2 | tbsp | dill | produce | chopped
      | | salt | spices*
      | | black pepper | spices*
      """, [
          "Heat oven to 425°F. Toss potatoes with 2 tbsp oil, salt and pepper; roast 20 minutes.",
          "Push potatoes aside; add green beans and salmon. Brush salmon with remaining oil mixed with garlic and lemon zest.",
          "Roast until salmon flakes, 12 to 14 minutes.",
          "Finish with lemon juice and dill.",
      ]),
    R("Fish Tacos with Lime Slaw", "Crispy spiced cod tucked into tortillas with tangy slaw and chipotle mayo.",
      4, 30, "Mexican", "fish", "tacos, weeknight", """
      1.5 | lb | cod fillet | seafood
      1 | tsp | chili powder | spices*
      1 | tsp | ground cumin | spices*
      0.5 | cup | all-purpose flour | pantry*
      3 | tbsp | neutral oil | pantry*
      8 | | corn tortilla | bakery
      3 | cup | shredded cabbage | produce
      2 | | lime | produce
      0.33 | cup | mayonnaise | pantry
      1 | tbsp | chipotle in adobo | pantry | minced
      1 | | avocado | produce
      0.5 | cup | cilantro | produce
      | | salt | spices*
      """, [
          "Toss cabbage with juice of 1 lime and salt.",
          "Mix mayonnaise and chipotle.",
          "Season cod with spices and salt, dredge in flour, and pan-fry in oil until golden and flaky, 3 minutes per side.",
          "Fill warm tortillas with fish, slaw, avocado, chipotle mayo and cilantro.",
      ]),
    R("Garlic Butter Shrimp Scampi", "Classic shrimp scampi with linguine, lemon and white wine.",
      4, 25, "Italian", "shellfish", "pasta, quick", """
      1 | lb | linguine | pantry
      1.25 | lb | large shrimp | seafood | peeled and deveined
      4 | tbsp | butter | dairy*
      2 | tbsp | olive oil | pantry*
      6 | clove | garlic | produce | sliced
      0.5 | tsp | red pepper flakes | spices*
      0.5 | cup | dry white wine | pantry
      1 | | lemon | produce
      0.33 | cup | parsley | produce | chopped
      | | salt | spices*
      """, [
          "Cook linguine in salted water; reserve 1 cup pasta water.",
          "Sear shrimp in oil 1 minute per side; remove.",
          "Melt butter with garlic and pepper flakes; add wine and simmer 2 minutes.",
          "Toss in pasta, shrimp, lemon juice and pasta water as needed. Finish with parsley.",
      ]),
    R("Coconut Shrimp Curry", "Fragrant shrimp simmered in a coconut, tomato and spice sauce.",
      4, 30, "Indian", "shellfish", "curry, weeknight", """
      1.25 | lb | large shrimp | seafood | peeled
      1 | | yellow onion | produce | diced
      3 | clove | garlic | produce | minced
      1 | tbsp | ginger | produce | grated
      2 | tbsp | curry powder | spices*
      1 | can | diced tomatoes | pantry
      1 | can | coconut milk | pantry
      2 | tbsp | neutral oil | pantry*
      5 | oz | baby spinach | produce
      1.5 | cup | basmati rice | pantry
      1 | | lime | produce
      | | salt | spices*
      """, [
          "Cook rice. Sauté onion in oil until soft, 6 minutes; add garlic, ginger and curry powder for 1 minute.",
          "Add tomatoes and coconut milk; simmer 10 minutes.",
          "Add shrimp and spinach; cook until shrimp are pink, 3 to 4 minutes.",
          "Season with salt and lime juice; serve over rice.",
      ]),
    R("Mediterranean Baked Cod", "Cod baked over tomatoes, olives and capers with crusty bread.",
      4, 30, "Mediterranean", "fish", "one-pan, light", """
      1.5 | lb | cod fillet | seafood
      2 | pint | cherry tomatoes | produce
      0.5 | cup | kalamata olives | pantry
      2 | tbsp | capers | pantry
      3 | clove | garlic | produce | sliced
      3 | tbsp | olive oil | pantry*
      1 | | lemon | produce
      0.25 | cup | parsley | produce
      1 | | crusty bread loaf | bakery
      | | salt | spices*
      """, [
          "Heat oven to 400°F. Toss tomatoes, olives, capers and garlic with oil in a baking dish; roast 15 minutes.",
          "Nestle in seasoned cod, spoon juices over, and add lemon slices.",
          "Bake until cod flakes, 10 to 12 minutes. Top with parsley and serve with bread.",
      ]),
    R("Salmon Cakes with Herby Yogurt", "Crispy salmon cakes with a lemony yogurt sauce and simple salad.",
      4, 35, "American", "fish", "pan-fried, light", """
      1.25 | lb | salmon fillet | seafood | skinless, finely chopped
      0.5 | cup | panko breadcrumbs | pantry
      1 | | egg | dairy
      2 | tbsp | mayonnaise | pantry
      1 | tbsp | dijon mustard | pantry
      2 | | scallion | produce
      1 | | lemon | produce
      0.75 | cup | greek yogurt | dairy
      2 | tbsp | dill | produce
      5 | oz | mixed greens | produce
      2 | tbsp | neutral oil | pantry*
      | | salt | spices*
      """, [
          "Mix salmon, panko, egg, mayo, mustard, scallions, lemon zest and salt; form 8 patties and chill 10 minutes.",
          "Stir yogurt with dill, lemon juice and salt.",
          "Fry cakes in oil over medium until golden, 3 to 4 minutes per side.",
          "Serve with greens and yogurt sauce.",
      ]),
    R("Shrimp and Grits", "Creamy cheddar grits topped with smoky, garlicky shrimp.",
      4, 30, "Southern", "shellfish", "comfort", """
      1 | cup | stone-ground grits | pantry
      4 | cup | whole milk | dairy
      4 | oz | sharp cheddar | dairy | grated
      1.25 | lb | large shrimp | seafood | peeled
      4 | slice | bacon | meat | chopped
      3 | clove | garlic | produce | minced
      1 | tsp | smoked paprika | spices*
      3 | | scallion | produce
      1 | | lemon | produce
      2 | tbsp | butter | dairy*
      | | salt | spices*
      """, [
          "Simmer grits in milk and 1 cup water, whisking often, until thick, 20 minutes. Stir in cheddar and butter.",
          "Crisp bacon; remove, leaving fat.",
          "Cook shrimp, garlic and paprika in bacon fat until pink, 3 minutes. Add lemon juice.",
          "Spoon shrimp over grits; top with bacon and scallions.",
      ]),

    # ---------------- chicken & turkey ----------------
    R("Lemon Chicken Orzo", "One-pot chicken with orzo, spinach, lemon and parmesan.",
      4, 35, "Mediterranean", "chicken", "one-pot, weeknight", """
      1.5 | lb | boneless chicken thighs | meat | bite-size pieces
      2 | tbsp | olive oil | pantry*
      1 | | yellow onion | produce | diced
      3 | clove | garlic | produce | minced
      1.5 | cup | orzo | pantry
      4 | cup | chicken broth | pantry
      1 | | lemon | produce
      5 | oz | baby spinach | produce
      0.5 | cup | parmesan | dairy
      | | salt | spices*
      | | black pepper | spices*
      """, [
          "Brown seasoned chicken in oil; remove.",
          "Cook onion 4 minutes, add garlic and orzo and toast 1 minute.",
          "Add broth and chicken; simmer, stirring, until orzo is tender, 12 minutes.",
          "Stir in spinach, lemon zest and juice and parmesan.",
      ]),
    R("Chicken Tikka Masala", "Charred yogurt-marinated chicken in a creamy spiced tomato sauce.",
      4, 45, "Indian", "chicken", "curry, crowd-pleaser", """
      1.5 | lb | boneless chicken thighs | meat
      0.5 | cup | greek yogurt | dairy
      1 | tbsp | garam masala | spices*
      1 | tsp | ground turmeric | spices*
      2 | tbsp | butter | dairy*
      1 | | yellow onion | produce | diced
      4 | clove | garlic | produce
      1 | tbsp | ginger | produce
      1 | can | crushed tomatoes | pantry
      0.5 | cup | heavy cream | dairy
      1.5 | cup | basmati rice | pantry
      0.5 | cup | cilantro | produce
      | | salt | spices*
      """, [
          "Marinate chicken in yogurt, half the garam masala, turmeric and salt for 15+ minutes.",
          "Broil chicken until charred in spots, 10 minutes; cut into pieces.",
          "Cook onion in butter until golden; add garlic, ginger and remaining garam masala.",
          "Add tomatoes, simmer 10 minutes, stir in cream and chicken. Serve with rice and cilantro.",
      ]),
    R("Sheet-Pan Chicken Fajitas", "Smoky chicken, peppers and onions roasted on one pan.",
      4, 30, "Mexican", "chicken", "sheet-pan, tacos, weeknight", """
      1.5 | lb | boneless chicken breast | meat | sliced
      3 | | bell pepper | produce | sliced
      1 | | yellow onion | produce | sliced
      3 | tbsp | olive oil | pantry*
      2 | tsp | chili powder | spices*
      1 | tsp | ground cumin | spices*
      1 | tsp | smoked paprika | spices*
      8 | | flour tortilla | bakery
      1 | | lime | produce
      0.5 | cup | sour cream | dairy
      1 | | avocado | produce
      | | salt | spices*
      """, [
          "Heat oven to 425°F. Toss chicken, peppers and onion with oil, spices and salt.",
          "Roast on a sheet pan 20 minutes, then broil 2 minutes for char.",
          "Squeeze lime over and serve in warm tortillas with sour cream and avocado.",
      ]),
    R("Turkey Taco Lettuce Wraps", "Spiced ground turkey in crunchy lettuce cups with pico de gallo.",
      4, 20, "Mexican", "turkey", "quick, low-carb", """
      1.25 | lb | ground turkey | meat
      1 | tbsp | neutral oil | pantry*
      2 | tsp | chili powder | spices*
      1 | tsp | ground cumin | spices*
      2 | head | butter lettuce | produce
      2 | | tomato | produce | diced
      0.25 | | red onion | produce | diced
      1 | | lime | produce
      1 | | avocado | produce
      4 | oz | cheddar | dairy | shredded
      | | salt | spices*
      """, [
          "Brown turkey in oil, breaking it up; add spices, salt and a splash of water and simmer 2 minutes.",
          "Mix tomato, onion, lime juice and salt for a quick pico.",
          "Spoon turkey into lettuce leaves; top with pico, avocado and cheddar.",
      ]),
    R("Honey Garlic Chicken Thighs", "Sticky glazed thighs with roasted broccoli and rice.",
      4, 35, "Asian", "chicken", "weeknight, kid-friendly", """
      2 | lb | boneless chicken thighs | meat
      0.33 | cup | honey | pantry
      0.25 | cup | soy sauce | pantry*
      4 | clove | garlic | produce | minced
      1 | tbsp | rice vinegar | pantry*
      1 | head | broccoli | produce
      2 | tbsp | neutral oil | pantry*
      1.5 | cup | jasmine rice | pantry
      | | salt | spices*
      """, [
          "Cook rice. Roast broccoli with 1 tbsp oil and salt at 425°F, 18 minutes.",
          "Sear seasoned chicken in remaining oil until browned and cooked, 6 minutes per side.",
          "Add honey, soy, garlic and vinegar; simmer, turning chicken, until sticky.",
          "Serve with rice and broccoli.",
      ]),

    # ---------------- beef, pork, lamb ----------------
    R("Korean Beef Bowls", "Sweet-savory ground beef over rice with quick-pickled cucumbers.",
      4, 20, "Korean", "beef", "bowl, quick", """
      1 | lb | ground beef | meat
      3 | clove | garlic | produce | minced
      1 | tbsp | ginger | produce | grated
      0.25 | cup | soy sauce | pantry*
      2 | tbsp | brown sugar | pantry*
      1 | tbsp | gochujang | pantry
      1 | tsp | toasted sesame oil | pantry
      1 | | english cucumber | produce | thinly sliced
      2 | tbsp | rice vinegar | pantry*
      3 | | scallion | produce
      1.5 | cup | jasmine rice | pantry
      """, [
          "Cook rice. Toss cucumber with vinegar and a pinch of salt and sugar.",
          "Brown beef; add garlic and ginger for 1 minute.",
          "Stir in soy, sugar, gochujang and sesame oil; simmer 2 minutes.",
          "Serve over rice with cucumbers and scallions.",
      ]),
    R("Steak Frites with Herb Butter", "Seared strip steak with oven fries and a garlicky herb butter.",
      2, 45, "French", "beef", "date-night", """
      2 | | strip steak | meat | about 12 oz each
      1.5 | lb | russet potatoes | produce | cut into fries
      3 | tbsp | neutral oil | pantry*
      3 | tbsp | butter | dairy* | softened
      1 | clove | garlic | produce | grated
      2 | tbsp | parsley | produce
      5 | oz | arugula | produce
      1 | | lemon | produce
      | | salt | spices*
      | | black pepper | spices*
      """, [
          "Heat oven to 450°F. Toss fries with 2 tbsp oil and salt; roast 30 minutes, flipping once.",
          "Mash butter with garlic, parsley and salt.",
          "Season steaks generously and sear in remaining oil over high heat, 4 minutes per side for medium-rare. Rest 5 minutes.",
          "Top steak with herb butter; serve with fries and lemony arugula.",
      ]),
    R("Pork Carnitas Tacos", "Oven-braised, crisped pork shoulder with onion, cilantro and salsa verde.",
      6, 180, "Mexican", "pork", "weekend, make-ahead, tacos", """
      3 | lb | pork shoulder | meat | 2-inch chunks
      1 | | orange | produce
      1 | | yellow onion | produce | quartered
      4 | clove | garlic | produce
      2 | tsp | ground cumin | spices*
      1 | tsp | dried oregano | spices*
      12 | | corn tortilla | bakery
      1 | cup | salsa verde | pantry
      0.5 | cup | cilantro | produce
      1 | | white onion | produce | diced
      2 | | lime | produce
      | | salt | spices*
      """, [
          "Heat oven to 325°F. Combine pork, orange juice and halves, onion, garlic, spices, 2 tsp salt and 1 cup water in a Dutch oven.",
          "Cover and braise until tender, about 2 1/2 hours.",
          "Shred pork, spread on a sheet pan with some juices and broil until crisp.",
          "Serve in tortillas with salsa verde, white onion, cilantro and lime.",
      ]),
    R("Sausage, White Bean and Kale Skillet", "Browned Italian sausage with creamy white beans and garlicky kale.",
      4, 25, "Italian", "pork", "one-pan, quick", """
      1 | lb | italian sausage | meat | casings removed
      1 | bunch | lacinato kale | produce | chopped
      2 | can | cannellini beans | pantry | drained
      3 | clove | garlic | produce | sliced
      1 | cup | chicken broth | pantry
      0.5 | cup | parmesan | dairy
      1 | | crusty bread loaf | bakery
      1 | tbsp | olive oil | pantry*
      | | salt | spices*
      """, [
          "Brown sausage in oil, breaking into pieces.",
          "Add garlic and kale; cook until wilted.",
          "Add beans and broth; simmer until creamy, 8 minutes.",
          "Top with parmesan; serve with bread.",
      ]),
    R("Pork Chops with Apples and Onions", "Juicy seared pork chops with sweet sautéed apples and mustard pan sauce.",
      4, 30, "American", "pork", "fall, one-pan", """
      4 | | bone-in pork chop | meat
      2 | | apple | produce | sliced
      1 | | yellow onion | produce | sliced
      2 | tbsp | butter | dairy*
      1 | tbsp | neutral oil | pantry*
      0.75 | cup | chicken broth | pantry
      1 | tbsp | dijon mustard | pantry
      1 | tsp | fresh thyme | produce
      | | salt | spices*
      | | black pepper | spices*
      """, [
          "Season chops and sear in oil over medium-high, 4 to 5 minutes per side; rest.",
          "Melt butter, cook apples and onion with thyme until soft and golden, 8 minutes.",
          "Add broth and mustard; simmer until slightly reduced.",
          "Return chops and juices to the pan and spoon sauce over.",
      ]),
    R("Greek Lamb Meatballs", "Herby lamb meatballs with tzatziki, pita and a chopped salad.",
      4, 35, "Greek", "lamb", "meatballs, weeknight", """
      1.25 | lb | ground lamb | meat
      0.25 | | red onion | produce | grated
      2 | clove | garlic | produce | grated
      0.25 | cup | parsley | produce
      2 | tbsp | mint | produce
      1 | tsp | ground cumin | spices*
      1 | cup | greek yogurt | dairy
      1 | | english cucumber | produce
      1 | | lemon | produce
      4 | | pita | bakery
      1 | cup | cherry tomatoes | produce
      | | salt | spices*
      """, [
          "Mix lamb, onion, garlic, herbs, cumin and salt; roll into 16 meatballs.",
          "Roast at 425°F until browned, 15 minutes.",
          "Grate half the cucumber into yogurt with lemon juice and salt for tzatziki.",
          "Chop remaining cucumber with tomatoes. Serve meatballs with warm pita, tzatziki and salad.",
      ]),
    R("Beef and Broccoli", "Takeout-style stir-fry with tender flank steak and crisp broccoli.",
      4, 25, "Chinese", "beef", "stir-fry, weeknight", """
      1.25 | lb | flank steak | meat | thinly sliced against the grain
      1 | tbsp | cornstarch | pantry
      1 | head | broccoli | produce | florets
      0.25 | cup | soy sauce | pantry*
      2 | tbsp | oyster sauce | pantry
      1 | tbsp | brown sugar | pantry*
      3 | clove | garlic | produce | minced
      1 | tbsp | ginger | produce | grated
      2 | tbsp | neutral oil | pantry*
      1.5 | cup | jasmine rice | pantry
      """, [
          "Cook rice. Toss beef with cornstarch.",
          "Whisk soy, oyster sauce, sugar and 1/3 cup water.",
          "Sear beef in batches in hot oil; remove. Stir-fry broccoli with a splash of water until bright, 3 minutes.",
          "Add garlic and ginger, then sauce and beef; toss until glossy. Serve over rice.",
      ]),
]
