import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Return 204 No Content for /favicon.ico to avoid 404 noise
export function middleware(req: NextRequest) {
  return new NextResponse(null, { status: 204 });
}

export const config = {
  matcher: ['/favicon.ico'],
};
