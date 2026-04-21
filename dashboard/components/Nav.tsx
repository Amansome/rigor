import Link from "next/link";

export default function Nav() {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="max-w-4xl mx-auto px-6 h-12 flex items-center gap-6">
        <Link href="/" className="font-medium text-gray-900 hover:text-gray-600">
          Runs
        </Link>
        <Link href="/compare" className="font-medium text-gray-900 hover:text-gray-600">
          Compare
        </Link>
      </div>
    </nav>
  );
}
