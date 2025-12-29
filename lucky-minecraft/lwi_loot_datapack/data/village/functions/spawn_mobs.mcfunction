# One-time spawn mobs around chests
# Run: /function village:spawn_mobs
# WARNING: chunks must be loaded (destinations)!

# ---- Chest 1: 241 65 471 ----
execute in minecraft:overworld run summon minecraft:marker 241 65 471 {Tags:["village_tmp","village_c1","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 241 65 471 {Tags:["village_tmp","village_c1","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 241 65 471 {Tags:["village_tmp","village_c1","mob_skeleton"]}
execute in minecraft:overworld run summon minecraft:marker 241 65 471 {Tags:["village_tmp","village_c1","mob_spider"]}
execute in minecraft:overworld run spreadplayers 241 471 5 20 false @e[type=minecraft:marker,tag=village_tmp,tag=village_c1,distance=..1]
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c1,tag=mob_zombie] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:zombie ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c1,tag=mob_skeleton] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:skeleton ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c1,tag=mob_spider] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:spider ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld run kill @e[type=minecraft:marker,tag=village_tmp,tag=village_c1,distance=..25]

# ---- Chest 2: 225 65 497 ----
execute in minecraft:overworld run summon minecraft:marker 225 65 497 {Tags:["village_tmp","village_c2","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 225 65 497 {Tags:["village_tmp","village_c2","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 225 65 497 {Tags:["village_tmp","village_c2","mob_skeleton"]}
execute in minecraft:overworld run summon minecraft:marker 225 65 497 {Tags:["village_tmp","village_c2","mob_spider"]}
execute in minecraft:overworld run spreadplayers 225 497 5 20 false @e[type=minecraft:marker,tag=village_tmp,tag=village_c2,distance=..1]
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c2,tag=mob_zombie] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:zombie ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c2,tag=mob_skeleton] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:skeleton ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c2,tag=mob_spider] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:spider ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld run kill @e[type=minecraft:marker,tag=village_tmp,tag=village_c2,distance=..25]

# ---- Chest 3: 247 65 455 ----
execute in minecraft:overworld run summon minecraft:marker 247 65 455 {Tags:["village_tmp","village_c3","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 247 65 455 {Tags:["village_tmp","village_c3","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 247 65 455 {Tags:["village_tmp","village_c3","mob_skeleton"]}
execute in minecraft:overworld run summon minecraft:marker 247 65 455 {Tags:["village_tmp","village_c3","mob_spider"]}
execute in minecraft:overworld run spreadplayers 247 455 5 20 false @e[type=minecraft:marker,tag=village_tmp,tag=village_c3,distance=..1]
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c3,tag=mob_zombie] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:zombie ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c3,tag=mob_skeleton] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:skeleton ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c3,tag=mob_spider] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:spider ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld run kill @e[type=minecraft:marker,tag=village_tmp,tag=village_c3,distance=..25]

# ---- Chest 4: 218 65 450 ----
execute in minecraft:overworld run summon minecraft:marker 218 65 450 {Tags:["village_tmp","village_c4","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 218 65 450 {Tags:["village_tmp","village_c4","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 218 65 450 {Tags:["village_tmp","village_c4","mob_skeleton"]}
execute in minecraft:overworld run summon minecraft:marker 218 65 450 {Tags:["village_tmp","village_c4","mob_spider"]}
execute in minecraft:overworld run spreadplayers 218 450 5 20 false @e[type=minecraft:marker,tag=village_tmp,tag=village_c4,distance=..1]
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c4,tag=mob_zombie] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:zombie ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c4,tag=mob_skeleton] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:skeleton ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c4,tag=mob_spider] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:spider ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld run kill @e[type=minecraft:marker,tag=village_tmp,tag=village_c4,distance=..25]

# ---- Chest 5: 187 65 452 ----
execute in minecraft:overworld run summon minecraft:marker 187 65 452 {Tags:["village_tmp","village_c5","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 187 65 452 {Tags:["village_tmp","village_c5","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 187 65 452 {Tags:["village_tmp","village_c5","mob_skeleton"]}
execute in minecraft:overworld run summon minecraft:marker 187 65 452 {Tags:["village_tmp","village_c5","mob_spider"]}
execute in minecraft:overworld run spreadplayers 187 452 5 20 false @e[type=minecraft:marker,tag=village_tmp,tag=village_c5,distance=..1]
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c5,tag=mob_zombie] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:zombie ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c5,tag=mob_skeleton] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:skeleton ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c5,tag=mob_spider] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:spider ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld run kill @e[type=minecraft:marker,tag=village_tmp,tag=village_c5,distance=..25]

# ---- Chest 6: 174 65 472 ----
execute in minecraft:overworld run summon minecraft:marker 174 65 472 {Tags:["village_tmp","village_c6","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 174 65 472 {Tags:["village_tmp","village_c6","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 174 65 472 {Tags:["village_tmp","village_c6","mob_skeleton"]}
execute in minecraft:overworld run summon minecraft:marker 174 65 472 {Tags:["village_tmp","village_c6","mob_spider"]}
execute in minecraft:overworld run spreadplayers 174 472 5 20 false @e[type=minecraft:marker,tag=village_tmp,tag=village_c6,distance=..1]
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c6,tag=mob_zombie] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:zombie ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c6,tag=mob_skeleton] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:skeleton ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c6,tag=mob_spider] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:spider ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld run kill @e[type=minecraft:marker,tag=village_tmp,tag=village_c6,distance=..25]

# ---- Chest 7: 193 65 482 ----
execute in minecraft:overworld run summon minecraft:marker 193 65 482 {Tags:["village_tmp","village_c7","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 193 65 482 {Tags:["village_tmp","village_c7","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 193 65 482 {Tags:["village_tmp","village_c7","mob_skeleton"]}
execute in minecraft:overworld run summon minecraft:marker 193 65 482 {Tags:["village_tmp","village_c7","mob_spider"]}
execute in minecraft:overworld run spreadplayers 193 482 5 20 false @e[type=minecraft:marker,tag=village_tmp,tag=village_c7,distance=..1]
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c7,tag=mob_zombie] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:zombie ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c7,tag=mob_skeleton] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:skeleton ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c7,tag=mob_spider] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:spider ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld run kill @e[type=minecraft:marker,tag=village_tmp,tag=village_c7,distance=..25]

# ---- Chest 8: 162 65 485 ----
execute in minecraft:overworld run summon minecraft:marker 162 65 485 {Tags:["village_tmp","village_c8","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 162 65 485 {Tags:["village_tmp","village_c8","mob_zombie"]}
execute in minecraft:overworld run summon minecraft:marker 162 65 485 {Tags:["village_tmp","village_c8","mob_skeleton"]}
execute in minecraft:overworld run summon minecraft:marker 162 65 485 {Tags:["village_tmp","village_c8","mob_spider"]}
execute in minecraft:overworld run spreadplayers 162 485 5 20 false @e[type=minecraft:marker,tag=village_tmp,tag=village_c8,distance=..1]
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c8,tag=mob_zombie] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:zombie ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c8,tag=mob_skeleton] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:skeleton ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=village_tmp,tag=village_c8,tag=mob_spider] at @s if block ~ ~ ~ air unless block ~ ~-1 ~ air run summon minecraft:spider ~ ~ ~ {PersistenceRequired:1b}
execute in minecraft:overworld run kill @e[type=minecraft:marker,tag=village_tmp,tag=village_c8,distance=..25]
