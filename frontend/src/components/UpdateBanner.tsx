interface Props {
  version: string;
}

export default function UpdateBanner({ version }: Props) {
  return (
    <div className="mb-6 flex items-center justify-between bg-[#333665c7] border border-[#7287fd] text-[#cdd6f4] px-4 py-3 rounded-lg shadow-md">
      <span className="flex items-center gap-2 text-[#b4befe] font-medium">
        Update Available! (v{version})
      </span>

      <button
        className="bg-[#179299] hover:bg-[#209fb5] text-[#1e1e2e] px-3 py-1 rounded-md transition-colors duration-200"
        onClick={() =>
          window.open(
            "https://github.com/sr1k7nth/WinTrack/releases/latest",
            "_blank"
          )
        }
      >
        Download
      </button>
    </div>
  );
}