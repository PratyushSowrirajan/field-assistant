/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_WS_BASE_URL: string;
  readonly VITE_MAPBOX_TOKEN: string;
  readonly VITE_LEAF_CHECK_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
