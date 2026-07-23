/// <reference types="node" />
import 'dotenv/config';

const port = process.env.PORT || '4000';
const nodeEnv = process.env.NODE_ENV || 'development';

console.log(`Starting in ${nodeEnv} mode on port ${port}...`);
