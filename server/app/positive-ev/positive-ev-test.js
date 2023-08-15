import prisma from '../../models/prisma.js';
import { getPositiveEV } from './positive-ev-model.js';
async function findAndPrintUser() {
    const positive = await getPositiveEV()
    console.log(positive)
    try {
      const user = await prisma.lines.findFirst();
      console.log(user);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      await prisma.$disconnect();
    }
  }
  
  findAndPrintUser();