(() => {
  const canvas = document.querySelector("#ambient-grid");
  if (!canvas) return;

  const context = canvas.getContext("2d");
  if (!context) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const smallScreen = window.matchMedia("(max-width: 639px)");
  const saveData = navigator.connection?.saveData === true;

  const targetFrameTime = 1000 / 22;
  const columns = 28;
  const rows = 18;
  const forwardSpeed = 0.00032;
  let cssWidth = 0;
  let cssHeight = 0;
  let frameRequest = 0;
  let lastFrame = -Infinity;
  let isVisible = true;

  function resize() {
    const bounds = canvas.getBoundingClientRect();
    const pixelRatio = Math.min(window.devicePixelRatio || 1, 1.25);

    cssWidth = Math.max(1, Math.round(bounds.width));
    cssHeight = Math.max(1, Math.round(bounds.height));
    canvas.width = Math.round(cssWidth * pixelRatio);
    canvas.height = Math.round(cssHeight * pixelRatio);
    context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    draw(performance.now());
  }

  function point(column, depth, time) {
    const xPosition = column / columns;
    const xFromCentre = xPosition * 2 - 1;
    // Keep the top broad instead of pinching the mesh into a dome-like horizon.
    const perspective = 0.72 + depth * 0.38;
    const horizon = cssHeight * 0.13;
    const floorHeight = cssHeight * 0.82;
    const baseY = horizon + Math.pow(depth, 1.55) * floorHeight;
    const phase = time * 0.00034;

    const broadWave = Math.sin(xFromCentre * 4.2 + depth * 7.5 - phase * 2.1);
    const crossWave = Math.sin(xFromCentre * -7.4 + depth * 4.1 + phase * 1.4);
    // Keep a slight bend at the horizon, then let the waves strengthen below it.
    const waveStrength = 0.06 + 0.94 * Math.pow(depth, 1.55);
    const displacement = (broadWave * 0.72 + crossWave * 0.28)
      * waveStrength
      * 19;

    return {
      x: cssWidth * 0.5 + xFromCentre * cssWidth * 0.63 * perspective,
      y: baseY + displacement,
    };
  }

  function draw(time) {
    context.clearRect(0, 0, cssWidth, cssHeight);
    context.lineWidth = 1;

    // Advancing one row at a time creates an endless ground plane moving
    // towards the viewer. The perspective curve naturally accelerates it.
    const rowOffset = (time * forwardSpeed) % 1;
    const horizon = cssHeight * 0.13;
    const fadeEnd = cssHeight * 0.3;

    // Horizontal lines carry a quiet trace of the site's orange accent.
    context.beginPath();
    for (let row = 0; row <= rows; row += 1) {
      const depth = (row + rowOffset) / rows;
      if (depth > 1) continue;

      for (let column = 0; column <= columns; column += 1) {
        const current = point(column, depth, time);
        if (column === 0) context.moveTo(current.x, current.y);
        else context.lineTo(current.x, current.y);
      }
    }
    const horizontalStroke = context.createLinearGradient(0, horizon, 0, fadeEnd);
    horizontalStroke.addColorStop(0, "rgba(217, 78, 36, 0)");
    horizontalStroke.addColorStop(1, "rgba(217, 78, 36, 0.105)");
    context.strokeStyle = horizontalStroke;
    context.stroke();

    context.beginPath();
    for (let column = 0; column <= columns; column += 1) {
      for (let row = 0; row <= rows; row += 1) {
        const depth = row / rows;
        const current = point(column, depth, time);
        if (row === 0) context.moveTo(current.x, current.y);
        else context.lineTo(current.x, current.y);
      }
    }
    const verticalStroke = context.createLinearGradient(0, horizon, 0, fadeEnd);
    verticalStroke.addColorStop(0, "rgba(100, 116, 139, 0)");
    verticalStroke.addColorStop(1, "rgba(100, 116, 139, 0.095)");
    context.strokeStyle = verticalStroke;
    context.stroke();
  }

  function canAnimate() {
    return isVisible
      && !document.hidden
      && !reducedMotion.matches
      && !smallScreen.matches
      && !saveData;
  }

  function animate(time) {
    frameRequest = 0;
    if (!canAnimate()) return;

    if (time - lastFrame >= targetFrameTime) {
      draw(time);
      lastFrame = time;
    }
    frameRequest = requestAnimationFrame(animate);
  }

  function updateAnimation() {
    if (frameRequest) {
      cancelAnimationFrame(frameRequest);
      frameRequest = 0;
    }

    if (canAnimate()) {
      lastFrame = -Infinity;
      frameRequest = requestAnimationFrame(animate);
    } else {
      draw(0);
    }
  }

  const observer = new IntersectionObserver(([entry]) => {
    isVisible = entry.isIntersecting;
    updateAnimation();
  });

  observer.observe(canvas);
  document.addEventListener("visibilitychange", updateAnimation);
  reducedMotion.addEventListener("change", updateAnimation);
  smallScreen.addEventListener("change", updateAnimation);
  window.addEventListener("resize", resize, { passive: true });

  resize();
  updateAnimation();
})();
