import Fastify, { FastifyRequest } from 'fastify';

type Priority = 'low' | 'normal' | 'high';
interface Task { id: number; title: string; done: boolean; priority: Priority; }

const app = Fastify();
const tasks = new Map<number, Task>();   // СПІЛЬНЕ сховище, а не сесія клієнта
let nextId = 1;

// поля, спільні для схем; на створення title обов'язковий, решта — з усталеними
const fields = {
  title:    { type: 'string', minLength: 1, maxLength: 200 },
  done:     { type: 'boolean' },
  priority: { type: 'string', enum: ['low', 'normal', 'high'] },
} as const;
