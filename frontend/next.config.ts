import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here 
  module.exports = {
    webpack5: true,
    webpack: (config: any) => {
      config.resolve.fallback = { fs: false, path: false, crypto: false };
      return config;
    },
  };
  */
 
}

// module.exports = {
//   webpack5: true,
//   webpack: (config: any) => {
//     config.resolve.fallback = { fs: false, path: false, crypto: false };
//     return config;
//   },
// };

// module.exports = {
//   resolve: {
//     modules: [...],
//     fallback: {
//       fs: false,
//       path: false,
//       crypto: false
//     }
//   }
// };

export default nextConfig;
