package org.westos.entity;

public class PasswordREQ {
    //用户id
    private Integer userId;
    //原密码 or 新密码
    private String password;

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    @Override
    public String toString() {
        return "PasswordREQ{" +
                "userId=" + userId +
                ", password='" + password + '\'' +
                '}';
    }
}