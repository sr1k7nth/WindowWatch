import { useEffect, useState } from "react";

interface UpdateInfo {
  update_available: boolean;
  current_version: string;
  latest_version: string;
}

export function useUpdate() {
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);

  useEffect(() => {
    fetch("/api/update")
      .then(res => res.json())
      .then(data => {
        if (data.update_available) {
          setUpdateInfo(data);
        }
      })
      .catch(() => {});
  }, []);

  return updateInfo;
}