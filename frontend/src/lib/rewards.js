// Rewards and the profile star. Rewards come only from finishing tasks, never from using less
// help. A star is earned for every STAR_EVERY rewards, and stars are never taken away.
export const STAR_EVERY = 10;

// All the rewards they have picked, in every world, plus the testing button's pretend ones.
export function totalRewards(settings) {
  const picked = Object.values(settings.gameItems || {}).reduce((n, list) => n + list.length, 0);
  return picked + (Number(settings.demoRewards) || 0);
}

export const starsFor = (total) => Math.floor(total / STAR_EVERY);

// What the profile says about their stars. Calm words, no scores or ranks.
export function starMessage(stars) {
  if (stars === 0) return `Collect ${STAR_EVERY} rewards to earn your first star.`;
  if (stars === 1) return "Welcome, collector. You earned your first star.";
  return `${stars} stars. You keep collecting at your own pace.`;
}
