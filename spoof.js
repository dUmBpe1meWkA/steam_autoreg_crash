// === Dynamic spoof.js ===

// Random WebGL vendor/renderer
const vendors = [
  ["Intel Inc.", "Intel Iris OpenGL Engine"],
  ["NVIDIA Corporation", "NVIDIA GeForce GTX 1660 Ti"],
  ["AMD", "AMD Radeon RX 5700 XT"]
];
const chosen = vendors[Math.floor(Math.random() * vendors.length)];

// WebGL spoof
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function (parameter) {
  if (parameter === 37445) return chosen[0]; // vendor
  if (parameter === 37446) return chosen[1]; // renderer
  return getParameter.call(this, parameter);
};

// Canvas spoof (random shift)
const toDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function () {
  const context = this.getContext('2d');
  const shift = {
    r: Math.floor(Math.random() * 10),
    g: Math.floor(Math.random() * 10),
    b: Math.floor(Math.random() * 10),
    a: 0
  };
  const width = this.width;
  const height = this.height;
  const imageData = context.getImageData(0, 0, width, height);

  for (let i = 0; i < height; i++) {
    for (let j = 0; j < width; j++) {
      const index = (i * (width * 4)) + (j * 4);
      imageData.data[index + 0] += shift.r;
      imageData.data[index + 1] += shift.g;
      imageData.data[index + 2] += shift.b;
      imageData.data[index + 3] += shift.a;
    }
  }

  context.putImageData(imageData, 0, 0);
  return toDataURL.apply(this, arguments);
};

// Audio spoof
const copy = AudioBuffer.prototype.copyFromChannel;
AudioBuffer.prototype.copyFromChannel = function () {
  const result = copy.apply(this, arguments);
  for (let i = 0; i < result.length; i++) {
    result[i] += Math.random() * 0.0000001;
  }
  return result;
};

// navigator.webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => false });

// navigator.languages
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

// navigator.plugins
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });

// userAgentData spoof (random Chrome version)
const chromeVersion = 114 + Math.floor(Math.random() * 8); // 114-121
Object.defineProperty(navigator, 'userAgentData', {
  get: () => ({
    brands: [
      { brand: 'Chromium', version: chromeVersion.toString() },
      { brand: 'Google Chrome', version: chromeVersion.toString() },
    ],
    mobile: false,
    platform: 'Windows',
  }),
});
