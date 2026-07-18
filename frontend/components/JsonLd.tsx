/** Injects Django-generated JSON-LD verbatim. Schema is never built here. */
export default function JsonLd({ data }: { data: object[] | undefined }) {
  if (!data?.length) return null;
  return (
    <>
      {data.map((block, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(block) }}
        />
      ))}
    </>
  );
}
