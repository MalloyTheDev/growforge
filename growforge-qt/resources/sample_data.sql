-- FILE: growforge/data/sample_data.sql
-- GrowForge sample data — loaded on first launch to demonstrate features.
-- Includes: 2 environments, 3 plants (seed, clone, breeding cross), sample events.

-- Environments
INSERT INTO environments (name, env_type, medium, light_type, light_wattage, light_schedule, tent_size, notes)
VALUES ('Main Tent', 'Indoor Tent', 'Coco/Perlite Mix', 'LED (Quantum Board)', 480, '18/6', '4x4 ft', 'Primary flowering and veg tent with Samsung LM301H diodes.');

INSERT INTO environments (name, env_type, medium, light_type, light_wattage, light_schedule, tent_size, notes)
VALUES ('Clone & Veg Cabinet', 'Cabinet', 'Rockwool', 'T5 Fluorescent', 96, '18/6', '2x2 ft', 'Small cabinet for clones, seedlings, and mothers.');

-- Plants
-- Plant 1: From seed, currently in Vegetative
INSERT INTO plants (name, strain_name, plant_type, genetics_type, stage, environment_id, start_date, germ_date, veg_date, medium, pot_size, notes, is_mother, is_active)
VALUES ('Blue Dream #1', 'Blue Dream', 'Photoperiod', 'Feminized', 'Vegetative', 1,
        date('now', '-28 days'), date('now', '-28 days'), date('now', '-14 days'),
        'Coco/Perlite Mix', '3 gallon',
        'Healthy growth. Topped above 5th node on day 18. Starting LST.', 0, 1);

-- Plant 2: Clone from mother, currently in Flowering
INSERT INTO plants (name, strain_name, plant_type, genetics_type, stage, environment_id, start_date, veg_date, flower_date, medium, pot_size, notes, is_mother, is_active)
VALUES ('OG Kush Clone #3', 'OG Kush', 'Photoperiod', 'Clone', 'Flowering', 1,
        date('now', '-56 days'), date('now', '-56 days'), date('now', '-21 days'),
        'Coco/Perlite Mix', '5 gallon',
        'Flipped to 12/12 three weeks ago. Stretch phase complete. Dense bud sites forming.', 0, 1);

-- Plant 3: Mother plant for cloning
INSERT INTO plants (name, strain_name, plant_type, genetics_type, stage, environment_id, start_date, veg_date, medium, pot_size, notes, is_mother, is_active)
VALUES ('GSC Mother', 'Girl Scout Cookies (GSC)', 'Photoperiod', 'Feminized', 'Vegetative', 2,
        date('now', '-90 days'), date('now', '-80 days'),
        'Rockwool', '5 gallon',
        'Dedicated mother plant. Taken 3 batches of clones so far. Very vigorous.', 1, 1);

-- Sample events for Plant 1 (Blue Dream)
INSERT INTO events (plant_id, event_type, event_date, title, notes, ph, ec, temp, humidity, water_ml)
VALUES (1, 'Watering', datetime('now', '-2 days'), 'Watering', 'Regular watering with plain pH water.', 6.2, NULL, 24.5, 58.0, 500);

INSERT INTO events (plant_id, event_type, event_date, title, notes, ph, ec, temp, humidity)
VALUES (1, 'Feeding', datetime('now', '-5 days'), 'Veg Feed', 'Full strength veg nutes. Canna A+B at 3ml/L + Cal-Mag 2ml/L.', 5.9, 1.4, 25.0, 55.0);

INSERT INTO events (plant_id, event_type, event_date, title, notes)
VALUES (1, 'Training (Topping)', datetime('now', '-10 days'), 'Topped above 5th node', 'Clean cut with sterile razor. Two new branches already visible after 2 days.');

INSERT INTO events (plant_id, event_type, event_date, title, notes)
VALUES (1, 'Training (LST)', datetime('now', '-7 days'), 'Started LST', 'Bent main stem 90 degrees and tied to pot edge. Opened up the canopy nicely.');

INSERT INTO events (plant_id, event_type, event_date, title, notes)
VALUES (1, 'Stage Change', datetime('now', '-14 days'), 'Advanced to Vegetative', 'Plant has 4 sets of true leaves. Strong root development. Moved to main tent.');

-- Sample events for Plant 2 (OG Kush)
INSERT INTO events (plant_id, event_type, event_date, title, notes, ph, ec, temp, humidity)
VALUES (2, 'Feeding', datetime('now', '-1 day'), 'Bloom Feed', 'Bloom nutrients at full strength. PK booster added. Canna PK 13/14 at 1ml/L.', 5.8, 1.8, 23.0, 45.0);

INSERT INTO events (plant_id, event_type, event_date, title, notes)
VALUES (2, 'Stage Change', datetime('now', '-21 days'), 'Flipped to Flower', 'Switched to 12/12 light schedule. Plant height: 18 inches. Expecting stretch.');

INSERT INTO events (plant_id, event_type, event_date, title, notes)
VALUES (2, 'Observation', datetime('now', '-7 days'), 'Bud development check', 'White pistils everywhere. Trichome production starting on sugar leaves. Smells amazing — fuel and pine.');

-- Sample events for Plant 3 (GSC Mother)
INSERT INTO events (plant_id, event_type, event_date, title, notes)
VALUES (3, 'Clone Taken', datetime('now', '-14 days'), 'Clone batch #3', 'Took 6 cuttings from lower branches. Used Clonex gel + rapid rooters.');

INSERT INTO events (plant_id, event_type, event_date, title, notes)
VALUES (3, 'Pruning', datetime('now', '-30 days'), 'Maintenance prune', 'Removed crowded inner growth. Shaped for better light penetration and more clone sites.');

-- Clone batch from GSC Mother
INSERT INTO clone_batches (mother_plant_id, batch_name, cut_date, rooting_method, medium, num_cuts, notes)
VALUES (3, 'GSC Batch #3', date('now', '-14 days'), 'Rooting Gel + Rapid Rooter', 'Rapid Rooter plugs', 6, 'Latest batch from the GSC mother. Using dome with heat mat.');

INSERT INTO clones (batch_id, clone_name, stage, status, notes)
VALUES (1, 'GSC Batch #3 - #1', 'Rooting', 'Active', 'Looking healthy, slight wilt day 1-2 but recovered.');
INSERT INTO clones (batch_id, clone_name, stage, status, notes)
VALUES (1, 'GSC Batch #3 - #2', 'Rooting', 'Active', 'Roots visible through plug on day 10.');
INSERT INTO clones (batch_id, clone_name, stage, status, notes)
VALUES (1, 'GSC Batch #3 - #3', 'Rooting', 'Active', 'Slow but steady.');
INSERT INTO clones (batch_id, clone_name, stage, status, notes)
VALUES (1, 'GSC Batch #3 - #4', 'Cut Taken', 'Active', 'Latest cut, still fresh.');
INSERT INTO clones (batch_id, clone_name, stage, status, notes)
VALUES (1, 'GSC Batch #3 - #5', 'Rooting', 'Active', 'Good vigor.');
INSERT INTO clones (batch_id, clone_name, stage, status, notes)
VALUES (1, 'GSC Batch #3 - #6', 'Cut Taken', 'Dead', 'Did not survive — possible air embolism.');

-- Breeding cross
INSERT INTO crosses (cross_name, mother_strain, father_strain, pollination_date, seed_count, generation, goals, notes)
VALUES ('Blue Cookies', 'Girl Scout Cookies (GSC)', 'Blue Dream', date('now', '-60 days'), 24, 'F1',
        'Combine GSC frost and flavor with Blue Dream vigor and yield.',
        'Collected pollen from a Blue Dream male. Applied to one lower branch of GSC mother. Seeds harvested and dried.');

-- Phenotype from the cross
INSERT INTO phenotypes (cross_id, pheno_name, vigor_score, structure_score, yield_score, terpene_score, resin_score,
                        pest_resistance_score, mold_resistance_score, bag_appeal_score, potency_score, flavor_score,
                        overall_score, is_keeper, flowering_days, notes)
VALUES (1, 'Blue Cookies #7', 8, 7, 8, 9, 9, 7, 6, 9, 8, 9, 8.0, 1, 63,
        'Outstanding terpene profile — sweet berry cookies. Dense frosty colas. Keeper material for sure.');

-- Reminders
INSERT INTO reminders (plant_id, reminder_type, due_date, message, is_recurring, recurrence_days, is_completed)
VALUES (1, 'Watering', datetime('now', '+1 day'), 'Water Blue Dream #1', 1, 2, 0);

INSERT INTO reminders (plant_id, reminder_type, due_date, message, is_recurring, recurrence_days, is_completed)
VALUES (2, 'Feeding', datetime('now', '+2 days'), 'Feed OG Kush Clone #3 (bloom nutes)', 1, 4, 0);

INSERT INTO reminders (plant_id, reminder_type, due_date, message, is_recurring, recurrence_days, is_completed)
VALUES (2, 'Check', datetime('now', '+14 days'), 'Check trichomes on OG Kush — may be near harvest', 0, 0, 0);
