/**
 * Birthday World Behavior Pack - Main Entry Point
 *
 * This script handles all interactive gameplay elements:
 * - Welcome sequence with fireworks and personalized letter
 * - Photo gallery / Memory Museum
 * - 14 hidden birthday gifts tracking
 * - Treasure hunt with clues
 * - Birthday cake interaction
 * - Voice message playback
 * - Grand finale celebration
 *
 * API: @minecraft/server@2.11.0, @minecraft/server-ui@2.7.0
 * Target: Minecraft Bedrock 1.26.60 (package 1.26.6005)
 */

import { world, system, Player, Block, Entity, Vector3, ItemStack, MinecraftItemTypes, GameMode, DisplaySlotId, ObjectiveSortOrder, ScoreboardIdentity } from "@minecraft/server";
import { ActionFormData, ModalFormData, MessageFormData } from "@minecraft/server-ui";

// ============================================================================
// CONFIGURATION (injected at build time)
// ============================================================================

const CONFIG = {
  birthdayPerson: "Ujan",
  age: 14,
  totalGifts: 14,
  totalClues: 7,
  zones: {
    spawn: { name: "Grand Birthday Kingdom", center: { x: 0, y: 64, z: 0 }, radius: 50 },
    celebrationHall: { name: "Royal Celebration Hall", center: { x: 100, y: 64, z: 0 }, radius: 40 },
    memoryMuseum: { name: "Memory Museum", center: { x: -100, y: 64, z: 0 }, radius: 40 },
    amusementCity: { name: "Amusement & Adventure City", center: { x: 0, y: 64, z: 100 }, radius: 50 },
    mysteryForest: { name: "Mystery Forest", center: { x: 0, y: 64, z: -100 }, radius: 50 },
    secretVault: { name: "Secret Birthday Vault", center: { x: 200, y: 64, z: 200 }, radius: 30 },
    finaleArena: { name: "Grand Finale Arena", center: { x: -200, y: 64, z: -200 }, radius: 40 }
  }
};

// ============================================================================
// SCOREBOARD KEYS (per-player persistent tracking)
// ============================================================================

const SB_KEYS = {
  giftsFound: "birthday.gifts_found",
  cluesFound: "birthday.clues_found",
  currentClue: "birthday.current_clue",
  cakeInteracted: "birthday.cake_interacted",
  finaleReached: "birthday.finale_reached",
  voicePlayed: "birthday.voice_played",
  firstJoin: "birthday.first_join",
  museumVisited: "birthday.museum_visited"
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function getScore(player, key) {
  try {
    const obj = world.scoreboard.getObjective(key);
    if (!obj) return 0;
    const identity = player.scoreboardIdentity;
    return obj.getScore(identity) ?? 0;
  } catch (e) {
    return 0;
  }
}

function setScore(player, key, value) {
  try {
    let obj = world.scoreboard.getObjective(key);
    if (!obj) {
      obj = world.scoreboard.addObjective(key, key);
    }
    const identity = player.scoreboardIdentity;
    obj.setScore(identity, value);
  } catch (e) {
    console.warn(`Failed to set score ${key}:`, e);
  }
}

function addScore(player, key, delta = 1) {
  try {
    let obj = world.scoreboard.getObjective(key);
    if (!obj) {
      obj = world.scoreboard.addObjective(key, key);
    }
    const identity = player.scoreboardIdentity;
    obj.addScore(identity, delta);
  } catch (e) {
    console.warn(`Failed to add score ${key}:`, e);
  }
}

function getWorldProperty(key, defaultValue = undefined) {
  try {
    return world.getDynamicProperty(key) ?? defaultValue;
  } catch (e) {
    return defaultValue;
  }
}

function setWorldProperty(key, value) {
  try {
    world.setDynamicProperty(key, value);
  } catch (e) {
    console.warn(`Failed to set world property ${key}:`, e);
  }
}

function broadcastToPlayer(player, message) {
  player.sendMessage(`§6[Birthday] §r${message}`);
}

function playSound(player, soundId, options = {}) {
  try {
    player.playSound(soundId, { volume: 1.0, pitch: 1.0, ...options });
  } catch (e) {
    console.warn(`Failed to play sound ${soundId}:`, e);
  }
}

function playSoundAt(dimension, location, soundId, options = {}) {
  try {
    dimension.playSound(soundId, location, { volume: 1.0, ...options });
  } catch (e) {
    console.warn(`Failed to play sound at location:`, e);
  }
}

function showTitle(player, title, options = {}) {
  try {
    player.onScreenDisplay.setTitle(title, {
      subtitle: options.subtitle,
      fadeInDuration: options.fadeInDuration ?? 20,
      stayDuration: options.stayDuration ?? 100,
      fadeOutDuration: options.fadeOutDuration ?? 20
    });
  } catch (e) {
    console.warn("Failed to show title:", e);
  }
}

function showActionBar(player, message) {
  try {
    player.onScreenDisplay.setActionBar(message);
  } catch (e) {
    console.warn("Failed to show action bar:", e);
  }
}

function spawnFirework(dimension, location) {
  try {
    dimension.spawnParticle("minecraft:firework_explode", location);
  } catch (e) {
    console.warn("Failed to spawn firework:", e);
  }
}

function showFireworkDisplay(dimension, center, count = 20) {
  for (let i = 0; i < count; i++) {
    system.runTimeout(() => {
      const offset = {
        x: center.x + (Math.random() - 0.5) * 20,
        y: center.y + 10 + Math.random() * 10,
        z: center.z + (Math.random() - 0.5) * 20
      };
      dimension.spawnParticle("minecraft:firework_explode", offset);
      playSoundAt(dimension, offset, "birthday_firework_explode");
    }, i * 300);
  }
}

function giveItem(player, itemType, count = 1, customName = "", lore = []) {
  try {
    const itemStack = new ItemStack(itemType, count);
    if (customName) itemStack.nameTag = customName;
    if (lore.length > 0) itemStack.setLore(lore);
    const inventory = player.getComponent("minecraft:inventory")?.container;
    if (inventory) {
      const remaining = inventory.addItem(itemStack);
      if (remaining.amount > 0) {
        player.dimension.spawnItem(remaining, player.location);
      }
    }
    return true;
  } catch (e) {
    console.warn(`Failed to give item ${itemType}:`, e);
    return false;
  }
}

function giveWrittenBook(player, title, author, pages) {
  try {
    const book = new ItemStack(MinecraftItemTypes.WrittenBook, 1);
    const bookComp = book.getComponent("minecraft:writable_book");
    if (bookComp) {
      bookComp.setTitle(title);
      bookComp.setAuthor(author);
      bookComp.setPages(pages);
    }
    const inventory = player.getComponent("minecraft:inventory")?.container;
    if (inventory) {
      const remaining = inventory.addItem(book);
      if (remaining.amount > 0) {
        player.dimension.spawnItem(remaining, player.location);
      }
    }
    return true;
  } catch (e) {
    console.warn("Failed to give written book:", e);
    return false;
  }
}

// ============================================================================
// WELCOME SEQUENCE
// ============================================================================

function handleFirstJoin(player) {
  const hasJoined = getScore(player, SB_KEYS.firstJoin) === 1;
  if (hasJoined) return;

  setScore(player, SB_KEYS.firstJoin, 1);

  // Initialize all tracking scores
  setScore(player, SB_KEYS.giftsFound, 0);
  setScore(player, SB_KEYS.cluesFound, 0);
  setScore(player, SB_KEYS.currentClue, 0);
  setScore(player, SB_KEYS.cakeInteracted, 0);
  setScore(player, SB_KEYS.finaleReached, 0);
  setScore(player, SB_KEYS.voicePlayed, 0);
  setScore(player, SB_KEYS.museumVisited, 0);

  // Set adventure mode
  try {
    player.setGameMode(GameMode.Adventure);
  } catch (e) {
    console.warn("Failed to set adventure mode:", e);
  }

  const dimension = world.getDimension("overworld");

  // Welcome sequence with delays
  system.runTimeout(() => {
    showTitle(player, `§l§e★ Happy ${CONFIG.age}th Birthday! ★`, {
      subtitle: `§dWelcome, ${CONFIG.birthdayPerson}!`,
      stayDuration: 120
    });
    playSound(player, "birthday_firework_launch");
    showFireworkDisplay(dimension, player.location, 15);
  }, 20);

  system.runTimeout(() => {
    broadcastToPlayer(player, "§dWelcome to your personalized birthday adventure world!");
    broadcastToPlayer(player, "§7Explore 7 magical zones, find 14 hidden gifts, and solve the treasure hunt!");
  }, 60);

  system.runTimeout(() => {
    giveBirthdayLetter(player);
  }, 100);

  system.runTimeout(() => {
    playVoiceMessage(player);
  }, 140);

  system.runTimeout(() => {
    broadcastToPlayer(player, "§aYour adventure begins at the §lGrand Birthday Kingdom§r§a!");
    broadcastToPlayer(player, "§7Follow the path to the §lRoyal Celebration Hall§r§7 to start exploring.");
  }, 180);
}

function giveBirthdayLetter(player) {
  const pages = [
    `§l§eHappy ${CONFIG.age}th Birthday, ${CONFIG.birthdayPerson}!§r\n\n§7Welcome to your very own birthday adventure world! This world was created especially for you with love.`,
    `§l§6Your Adventure Awaits§r\n\n§7Explore seven magical zones:\n§e1. §rGrand Birthday Kingdom - Your royal spawn palace\n§e2. §rRoyal Celebration Hall - Feast and festivities\n§e3. §rMemory Museum - Your photo gallery through the years\n§e4. §rAmusement & Adventure City - Rides and games\n§e5. §rMystery Forest - Treasure hunt awaits!\n§e6. §rSecret Birthday Vault - 14 hidden gifts\n§e7. §rGrand Finale Arena - The ultimate celebration`,
    `§l§dObjectives§r\n\n§a☐ §rFind all 14 birthday gifts\n§a☐ §rSolve 7 treasure hunt clues\n§a☐ §rVisit all 7 zones\n§a☐ §rMake a wish on the birthday cake\n§a☐ §rReach the Grand Finale Arena\n\n§7Use §e!help §rfor commands.`,
    `§l§eWith Love§r\n\n§7From your family & friends\n\n§oOctober 31, 2026`
  ];

  giveWrittenBook(player, `§l§eA Letter for ${CONFIG.birthdayPerson}`, "Birthday World", pages);
  broadcastToPlayer(player, `§dYou received a §lPersonalized Birthday Letter§r§d! Check your inventory.`);
  playSound(player, "birthday_gift_found");
}

function playVoiceMessage(player) {
  if (getScore(player, SB_KEYS.voicePlayed) === 1) return;

  setScore(player, SB_KEYS.voicePlayed, 1);
  playSound(player, "birthday_message", { volume: 1.0, pitch: 1.0 });
  broadcastToPlayer(player, `§e🎵 Playing birthday voice message...`);
}

// ============================================================================
// GIFT SYSTEM
// ============================================================================

const GIFT_LOCATIONS = [
  { x: 10, y: 64, z: 10, zone: "spawn", item: MinecraftItemTypes.Diamond, name: "§bBirthday Diamond", lore: ["§7Gift 1 of 14"] },
  { x: -15, y: 65, z: 5, zone: "spawn", item: MinecraftItemTypes.Emerald, name: "§aBirthday Emerald", lore: ["§7Gift 2 of 14"] },
  { x: 105, y: 64, z: 10, zone: "celebrationHall", item: MinecraftItemTypes.GoldenApple, name: "§6Golden Apple", lore: ["§7Gift 3 of 14", "§7§oA taste of royalty"] },
  { x: 95, y: 66, z: -5, zone: "celebrationHall", item: MinecraftItemTypes.EnchantedBook, name: "§dEnchanted Birthday Book", lore: ["§7Gift 4 of 14", "§7§oWisdom for the year ahead"] },
  { x: -105, y: 64, z: 15, zone: "memoryMuseum", item: MinecraftItemTypes.FireworkRocket, name: "§eCelebration Rocket", lore: ["§7Gift 5 of 14", "§7§oFor your own firework shows"] },
  { x: -90, y: 65, z: -10, zone: "memoryMuseum", item: MinecraftItemTypes.Diamond, name: "§bMemory Diamond", lore: ["§7Gift 6 of 14"] },
  { x: 5, y: 70, z: 105, zone: "amusementCity", item: MinecraftItemTypes.Emerald, name: "§aPark Emerald", lore: ["§7Gift 7 of 14"] },
  { x: -10, y: 68, z: 95, zone: "amusementCity", item: MinecraftItemTypes.GoldenApple, name: "§6Carousel Apple", lore: ["§7Gift 8 of 14"] },
  { x: 15, y: 64, z: -105, zone: "mysteryForest", item: MinecraftItemTypes.EnchantedBook, name: "§dForest Secrets", lore: ["§7Gift 9 of 14"] },
  { x: -20, y: 66, z: -95, zone: "mysteryForest", item: MinecraftItemTypes.FireworkRocket, name: "§eMystery Rocket", lore: ["§7Gift 10 of 14"] },
  { x: 205, y: 64, z: 205, zone: "secretVault", item: MinecraftItemTypes.Diamond, name: "§bVault Diamond", lore: ["§7Gift 11 of 14", "§7§oDeep in the secret vault"] },
  { x: 195, y: 65, z: 195, zone: "secretVault", item: MinecraftItemTypes.Emerald, name: "§aVault Emerald", lore: ["§7Gift 12 of 14"] },
  { x: -205, y: 64, z: -205, zone: "finaleArena", item: MinecraftItemTypes.GoldenApple, name: "§6Finale Apple", lore: ["§7Gift 13 of 14"] },
  { x: -195, y: 65, z: -195, zone: "finaleArena", item: MinecraftItemTypes.EnchantedBook, name: "§dGrand Finale Book", lore: ["§7Gift 14 of 14", "§7§oThe final gift!"] }
];

function checkGiftDiscovery(player, location) {
  const giftsFound = getScore(player, SB_KEYS.giftsFound);

  // Use world dynamic property for found gift indices (array stored as JSON)
  const foundData = getWorldProperty(`birthday:gifts_found_${player.name}`, "[]");
  const foundIndices = JSON.parse(foundData);

  for (let i = 0; i < GIFT_LOCATIONS.length; i++) {
    if (foundIndices.includes(i)) continue;

    const gift = GIFT_LOCATIONS[i];
    const dist = Math.sqrt(
      Math.pow(location.x - gift.x, 2) +
      Math.pow(location.y - gift.y, 2) +
      Math.pow(location.z - gift.z, 2)
    );

    if (dist < 3) {
      // Found a gift!
      foundIndices.push(i);
      setWorldProperty(`birthday:gifts_found_${player.name}`, JSON.stringify(foundIndices));

      const newCount = giftsFound + 1;
      setScore(player, SB_KEYS.giftsFound, newCount);

      giveItem(player, gift.item, 1, gift.name, gift.lore);
      broadcastToPlayer(player, `§l§a★ Gift Found! ★ §r§aYou found: ${gift.name}`);
      broadcastToPlayer(player, `§7Progress: ${newCount}/${CONFIG.totalGifts} gifts`);
      playSound(player, "birthday_gift_found");

      // Update scoreboard display
      updateGiftScoreboard(player, newCount);

      if (newCount === CONFIG.totalGifts) {
        broadcastToPlayer(player, `§l§6★ ALL ${CONFIG.totalGifts} GIFTS FOUND! ★`);
        broadcastToPlayer(player, "§eThe Secret Birthday Vault has been unlocked!");
        const dimension = world.getDimension("overworld");
        showFireworkDisplay(dimension, player.location, 20);
        playSound(player, "birthday_firework_explode", { volume: 1.0, pitch: 0.8 });
      }
      break;
    }
  }
}

function updateGiftScoreboard(player, count) {
  try {
    const obj = world.scoreboard.getObjective("birthdayGifts");
    if (obj) {
      obj.setScore(player.scoreboardIdentity, count);
    }
  } catch (e) {
    console.warn("Scoreboard update failed:", e);
  }
}

// ============================================================================
// TREASURE HUNT SYSTEM
// ============================================================================

const TREASURE_CLUES = [
  {
    id: 0,
    location: { x: 0, y: 64, z: 0 },
    text: "§l§eClue 1§r§e: Your journey begins at the heart of the kingdom.\n§7Look for the golden block beneath the birthday banner.",
    nextZone: "celebrationHall"
  },
  {
    id: 1,
    location: { x: 100, y: 64, z: 0 },
    text: "§l§eClue 2§r§e: Where feasts are held and friends gather round,\n§7Seek the cake that makes no sound.",
    nextZone: "memoryMuseum"
  },
  {
    id: 2,
    location: { x: -100, y: 64, z: 0 },
    text: "§l§eClue 3§r§e: Memories line the walls in frames so bright,\n§7Find the photo that glows in the night.",
    nextZone: "amusementCity"
  },
  {
    id: 3,
    location: { x: 0, y: 64, z: 100 },
    text: "§l§eClue 4§r§e: Rides and games and laughter near,\n§7The next clue waits at the Ferris wheel's rear.",
    nextZone: "mysteryForest"
  },
  {
    id: 4,
    location: { x: 0, y: 64, z: -100 },
    text: "§l§eClue 5§r§e: Deep in the forest, secrets hide,\n§7Follow the path where fireflies guide.",
    nextZone: "secretVault"
  },
  {
    id: 5,
    location: { x: 200, y: 64, z: 200 },
    text: "§l§eClue 6§r§e: The vault is near, but locked up tight,\n§7Find the key that gleams so bright.",
    nextZone: "finaleArena"
  },
  {
    id: 6,
    location: { x: -200, y: 64, z: -200 },
    text: "§l§eClue 7§r§e: The final destination, grand and true,\n§7The arena awaits - celebration for you!",
    nextZone: "finale"
  }
];

function checkClueDiscovery(player, location) {
  const currentClue = getScore(player, SB_KEYS.currentClue);

  if (currentClue >= TREASURE_CLUES.length) return;

  const clue = TREASURE_CLUES[currentClue];
  const dist = Math.sqrt(
    Math.pow(location.x - clue.location.x, 2) +
    Math.pow(location.y - clue.location.y, 2) +
    Math.pow(location.z - clue.location.z, 2)
  );

  if (dist < 5) {
    setScore(player, SB_KEYS.cluesFound, currentClue + 1);
    setScore(player, SB_KEYS.currentClue, currentClue + 1);

    broadcastToPlayer(player, `§l§d★ Clue Found! ★`);
    broadcastToPlayer(player, clue.text);
    playSound(player, "birthday_treasure_clue");

    if (currentClue + 1 < TREASURE_CLUES.length) {
      const nextClue = TREASURE_CLUES[currentClue + 1];
      system.runTimeout(() => {
        broadcastToPlayer(player, `§7Next zone: §l${CONFIG.zones[nextClue.nextZone]?.name || nextClue.nextZone}`);
      }, 40);
    } else {
      broadcastToPlayer(player, `§l§6★ TREASURE HUNT COMPLETE! ★`);
      broadcastToPlayer(player, "§eThe path to the Grand Finale Arena is revealed!");
      const dimension = world.getDimension("overworld");
      showFireworkDisplay(dimension, player.location, 10);
    }
  }
}

function showClueUI(player) {
  const currentClue = getScore(player, SB_KEYS.currentClue);
  const cluesFound = getScore(player, SB_KEYS.cluesFound);

  const form = new ActionFormData()
    .title("§l§eTreasure Hunt")
    .body(`§7Clues found: ${cluesFound}/${TREASURE_CLUES.length}\n\n` +
          (currentClue < TREASURE_CLUES.length
            ? `§eCurrent clue: ${TREASURE_CLUES[currentClue].text}`
            : "§aAll clues found! Head to the Grand Finale Arena!"))
    .button("§aClose");

  form.show(player).catch(console.error);
}

// ============================================================================
// BIRTHDAY CAKE INTERACTION
// ============================================================================

function handleCakeInteraction(player, block) {
  if (block.typeId !== "minecraft:cake") return;

  const hasInteracted = getScore(player, SB_KEYS.cakeInteracted) === 1;

  if (!hasInteracted) {
    setScore(player, SB_KEYS.cakeInteracted, 1);
    broadcastToPlayer(player, "§l§e★ Happy Birthday! ★");
    broadcastToPlayer(player, `§dYou made a wish on your birthday cake!`);
    playSound(player, "birthday_cake_interact");
    const dimension = world.getDimension("overworld");
    showFireworkDisplay(dimension, player.location, 8);

    // Give a special cake reward
    giveItem(player, MinecraftItemTypes.GoldenApple, 1, "§6Birthday Wish Apple", ["§7§oYour wish may come true..."]);
  } else {
    broadcastToPlayer(player, "§7You already made your birthday wish!");
    playSound(player, "birthday_cake_interact", { volume: 0.5, pitch: 1.2 });
  }
}

// ============================================================================
// ZONE DETECTION & ENTRY MESSAGES
// ============================================================================

function getCurrentZone(player) {
  for (const [key, zone] of Object.entries(CONFIG.zones)) {
    const dist = Math.sqrt(
      Math.pow(player.location.x - zone.center.x, 2) +
      Math.pow(player.location.z - zone.center.z, 2)
    );
    if (dist <= zone.radius) {
      return key;
    }
  }
  return "wilderness";
}

const lastZone = new Map();

function checkZoneEntry(player) {
  const currentZone = getCurrentZone(player);
  const playerName = player.name;

  if (lastZone.get(playerName) !== currentZone) {
    lastZone.set(playerName, currentZone);
    const zoneInfo = CONFIG.zones[currentZone];

    if (zoneInfo) {
      broadcastToPlayer(player, `§l§6» Entering: ${zoneInfo.name} «`);
      playSound(player, "birthday_treasure_clue", { volume: 0.5, pitch: 1.0 });

      // Special zone events
      if (currentZone === "memoryMuseum" && getScore(player, SB_KEYS.museumVisited) === 0) {
        setScore(player, SB_KEYS.museumVisited, 1);
        system.runTimeout(() => {
          broadcastToPlayer(player, "§dWelcome to the Memory Museum! Your photos are displayed here.");
        }, 20);
      }
    }
  }
}

// ============================================================================
// GRAND FINALE
// ============================================================================

function checkFinale(player) {
  const finaleZone = CONFIG.zones.finaleArena;
  const dist = Math.sqrt(
    Math.pow(player.location.x - finaleZone.center.x, 2) +
    Math.pow(player.location.z - finaleZone.center.z, 2)
  );

  if (dist <= finaleZone.radius && getScore(player, SB_KEYS.finaleReached) === 0) {
    setScore(player, SB_KEYS.finaleReached, 1);
    triggerFinale(player);
  }
}

function triggerFinale(player) {
  const dimension = world.getDimension("overworld");
  const finaleZone = CONFIG.zones.finaleArena;

  showTitle(player, "§l§6★ ★ ★ GRAND FINALE ★ ★ ★", {
    subtitle: `§eCongratulations, ${CONFIG.birthdayPerson}!`,
    stayDuration: 160
  });
  broadcastToPlayer(player, `§eCongratulations, ${CONFIG.birthdayPerson}! You've reached the Grand Finale!`);

  // Epic fireworks show
  showFireworkDisplay(dimension, finaleZone.center, 50);

  // Celebration music
  playSound(player, "birthday_celebration_music", { volume: 1.0, pitch: 1.0 });

  // Final rewards
  giveItem(player, MinecraftItemTypes.NetheriteIngot, 1, "§l§6Finale Champion Medal", ["§7Awarded for completing the birthday adventure"]);
  giveItem(player, MinecraftItemTypes.FireworkRocket, 64, "§eCelebration Fireworks", ["§7For your own shows!"]);

  system.runTimeout(() => {
    broadcastToPlayer(player, `§l§dHappy ${CONFIG.age}th Birthday, ${CONFIG.birthdayPerson}!`);
    broadcastToPlayer(player, "§7Thank you for playing! Your adventure is complete.");
  }, 100);
}

// ============================================================================
// EVENT HANDLERS
// ============================================================================

// Player join / first spawn
world.afterEvents.playerSpawn.subscribe((event) => {
  const player = event.player;

  // initialSpawn is true only on first join (not respawn)
  if (event.initialSpawn) {
    handleFirstJoin(player);
  }
});

// Player interact with block (after)
world.afterEvents.playerInteractWithBlock.subscribe((event) => {
  const { player, block } = event;

  // Cake interaction
  handleCakeInteraction(player, block);

  // Check for gift discovery (proximity-based on interaction location)
  checkGiftDiscovery(player, block.location);

  // Check for clue discovery
  checkClueDiscovery(player, block.location);

  // Check for finale
  checkFinale(player);
});

// Player interact with entity
world.afterEvents.playerInteractWithEntity.subscribe((event) => {
  const { player, entity } = event;
  // Could add special entity interactions here (NPCs, display entities, etc.)
});

// Chat commands
world.beforeEvents.chatSend.subscribe((event) => {
  const { message, sender } = event;

  if (message === "!clue" || message === "!clues") {
    event.cancel = true;
    showClueUI(sender);
  }

  if (message === "!gifts") {
    event.cancel = true;
    const giftsFound = getScore(sender, SB_KEYS.giftsFound);
    sender.sendMessage(`§eGifts found: ${giftsFound}/${CONFIG.totalGifts}`);
  }

  if (message === "!zone") {
    event.cancel = true;
    const zone = getCurrentZone(sender);
    sender.sendMessage(`§eCurrent zone: ${CONFIG.zones[zone]?.name || zone}`);
  }

  if (message === "!help" || message === "!birthday") {
    event.cancel = true;
    const form = new ActionFormData()
      .title("§l§eBirthday World Help")
      .body(
        "§l§6Commands:§r\n" +
        "§e!clue§r - Show current treasure hunt clue\n" +
        "§e!gifts§r - Show gifts found\n" +
        "§e!zone§r - Show current zone\n" +
        "§e!help§r - Show this help\n\n" +
        "§l§6Objectives:§r\n" +
        "§7• Find all 14 birthday gifts\n" +
        "§7• Solve 7 treasure hunt clues\n" +
        "§7• Visit all 7 zones\n" +
        "§7• Interact with the birthday cake\n" +
        "§7• Reach the Grand Finale Arena"
      )
      .button("§aClose");
    form.show(sender).catch(console.error);
  }
});

// Periodic zone checking (every second = 20 ticks)
system.runInterval(() => {
  for (const player of world.getPlayers()) {
    checkZoneEntry(player);
    checkFinale(player);
  }
}, 20);

// ============================================================================
// INITIALIZATION
// ============================================================================

function initialize() {
  console.log("§l§e[Birthday World] §rBehavior pack loaded successfully!");
  console.log(`§6Birthday person: ${CONFIG.birthdayPerson}, Age: ${CONFIG.age}`);
  console.log(`§6Total gifts: ${CONFIG.totalGifts}, Total clues: ${CONFIG.totalClues}`);

  // Initialize scoreboard for gift tracking
  try {
    const scoreboard = world.scoreboard;
    let obj = scoreboard.getObjective("birthdayGifts");
    if (!obj) {
      obj = scoreboard.addObjective("birthdayGifts", "§eBirthday Gifts Found");
    }
    obj.setDisplay(DisplaySlotId.Sidebar, ObjectiveSortOrder.Descending);
  } catch (e) {
    console.warn("Scoreboard setup:", e);
  }
}

initialize();

export { CONFIG, SB_KEYS, GIFT_LOCATIONS, TREASURE_CLUES };