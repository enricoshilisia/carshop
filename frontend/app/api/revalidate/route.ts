import { revalidatePath, revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

/**
 * Django POSTs { paths, tags, secret } here when an Offer/SeoPage changes.
 * We drop the ISR cache first; Django purges Cloudflare AFTER this returns —
 * order matters, or the edge re-caches the stale page.
 */
export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  if (!body || body.secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ ok: false }, { status: 401 });
  }
  const paths: string[] = Array.isArray(body.paths) ? body.paths : [];
  const tags: string[] = Array.isArray(body.tags) ? body.tags : [];
  for (const p of paths) revalidatePath(p);
  for (const t of tags) revalidateTag(t);
  return NextResponse.json({ ok: true, revalidated: { paths: paths.length, tags: tags.length } });
}
