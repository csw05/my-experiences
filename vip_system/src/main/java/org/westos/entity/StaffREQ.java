package org.westos.entity;

import java.io.Serializable;

public class StaffREQ implements Serializable {
    //姓名
    private String name;
    //账号
    private String username;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    @Override
    public String toString() {
        return "StaffREQ{" +
                "name='" + name + '\'' +
                ", username='" + username + '\'' +
                '}';
    }
}